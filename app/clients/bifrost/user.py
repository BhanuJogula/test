from app.clients.bifrost.admin import BifrostService, ResourceNotFoundError
from app.clients.bifrost.validate import validate
from app.context import Context
from app.exception import AppException
from app.filter import FilterWithSchema
from ddtrace import tracer
from fastapi import Request
from jsonschema import ValidationError

import app.openapi
import jsonschema
import re
import time


bifrostService = BifrostService()

spec = app.openapi.load()
if spec is None: 
    raise Exception("Could not load openapi spec in thumbnail.py")

filter = FilterWithSchema(spec)

def get_token(request_obj: Request) -> str:
    """Extracts the jwt from the http headers. Format must be Authorization: bearer JWT

    Args:
        request_obj (Request): http request

    Returns:
        str: The encoded jwt
    """

    auth_header = request_obj.headers.get("Authorization", "")
    if not auth_header:
        raise AppException('missing', event='Auth.Headers', status_code=401)
    header_split: str = auth_header.split(" ")
    if len(header_split) != 2:
        raise AppException('incorrect length', event='Auth.Headers', status_code=401)

    if header_split[0].lower() != "bearer":
        raise AppException('no bearer', event='Auth.Headers', status_code=401)
    
    return header_split[1]


async def bifrost(http_request, action, name, request={}, args={}):
    context = Context(http_request)
    context.set('name', name)
    context.set('action', action)

    request_body = {}
    if http_request.method != "GET" and len(await http_request.body()):
        request_body = await http_request.json()
    else:
        request_body = dict(http_request.query_params)

    # preprocess request_body
    for (name,spec) in request.items():
        if name not in request_body and 'default' in spec:
            request_body[name] = spec['default']

        rename_key = 'map_to'
        if name in request_body and rename_key in spec:
            val = request_body.pop(name)
            request_body[spec[rename_key]] = val

    # append extra args to request body
    for (key,val) in args.items():
        request_body[key] = val

    bifrostService = await Thumbnail.from_http(http_request=http_request)
    result = await bifrostService.call(action, args=request_body)

    result = filter.filter_response(http_request.scope["endpoint"].__name__, result)
    return result

@tracer.wrap()
async def request_args(http_request: Request, schema=None, args=None):
    validated_args = {}
    route_name = http_request.scope['route'].name

    routeData = schema or app.openapi.get_route(route_name) 
    required = []
    schema = {}

    #TODO: allow schema param to override openapi file

    body = await http_request.body()
    if http_request.method != "GET" and len(body):
        request_body = await http_request.json()
        Context(http_request).set('http.request_body', request_body)
        schema_request_body = routeData['requestBody']['content']['application/json']['schema']
        schema = schema_request_body['properties']

        if 'required' in schema_request_body:
            required = schema_request_body['required']

    else:
        request_body = dict(http_request.query_params)
        for param in routeData['parameters']:
            if param['in'] == 'path':
                continue

            schema[param['name']] = param['schema']
            if 'required' in param and param['required']:
                required.append(param['name'])
                
    args = args or {}


    # preprocess request_body
    for (name,spec) in schema.items():
        if type(spec) is str:
            spec = { 'type': spec }
        
        if name not in request_body:
            if 'default' in spec:
                request_body[name] = spec['default']
            elif name in required:
                raise AppException("failed to validate request arg. missing property: " + name, 
                    event='ValidateRequest', status_code=400)
        
        if name in request_body:
            val = request_body[name]

            try:
                jsonschema.validate(val, spec)
                validated_args[name] = val

            except ValidationError as e:
                raise AppException(f"failed to validate request arg. invalid property: {name}={val} : {e.message}",
                    event='ValidateRequest', status_code=400, data={name: val})
            except Exception as e:
                raise AppException(f"failed to validate request arg. unknown error: {name}={val} : {str(e)}",
                    event='ValidateRequest', status_code=400, data={name: val})

        # rename
        rename_key = 'map_to'
        if name in validated_args and rename_key in spec:
            val = validated_args.pop(name)
            validated_args[spec[rename_key]] = val


    # append extra args to request body
    for (key,val) in args.items():
        validated_args[key] = val
    
    return validated_args



class Thumbnail:
    def __init__(self, token, http_request=None, validated=False, brand=None):

        self.token: str = token
        self.validated: bool = validated
        self.http_request: Request = http_request
        self.brand: str = brand
    
    async def args(self, schema=None):
        return await request_args(self.http_request, schema=schema)

    @tracer.wrap()
    async def create(token, http_request=None):
        context = Context(http_request)
        context.set('name', http_request.scope['route'].name)

        start_time = time.time_ns()
        auth_result = await validate(token, context=context)

        brand = auth_result.token_data['brand']

        context.set_time('auth.duration', start_time)
        if auth_result.is_valid:
            thumbnail_svc = Thumbnail(
                token=token, 
                validated=True, 
                http_request=http_request, 
                brand=brand
            )
            return thumbnail_svc
        else:
            raise AppException(
                message=f'account does not have valid authorized token: {auth_result.message}: ',
                event='Auth.Ownership',
                status_code=403,
            )


    async def from_http(http_request):
        token = get_token(http_request) 
        return await Thumbnail.create(token=token, http_request=http_request)

    async def call(self, action, args=None):
        self.validated = False

        if not self.validated:
            auth_result = await validate(self.token)
            self.validated = auth_result.is_valid
            self.brand = auth_result.token_data['brand']

        if self.validated:
            if not args:
                args = {}

            bifrostService.brand = self.brand

            context = Context(self.http_request)
            try:
                start_time = time.time_ns()
                context.set('bifrost.action', action)
                context.set('bifrost.details.request', args)
                result = await bifrostService.call(action, args)

                # details - may add config so these are not on by default
                context.set('bifrost.details.response', result)
                context.set('bifrost.status', 1)
            except ResourceNotFoundError as error:
                context.set('bifrost.status', 0)
                raise AppException(f'resource not found: {str(error)}', event='Bifrost.NotFound', status_code=404)
            except Exception as error:
                context.set('bifrost.status', 0)
                raise AppException(str(error), event='Bifrost.Call', exception=error)
            finally:
                context.set_time('bifrost.duration', start_time)

            return result

        else:
            raise AppException('Failed authorization before Bifrost call', event='Auth.Bifrost', status_code=403)
