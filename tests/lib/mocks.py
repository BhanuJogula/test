from app.clients.bifrost.validate import TokenSubject, ValidationResult
from app.nf_token import Token
from app.context import Context
from starlette.datastructures import QueryParams, Headers
from urllib.parse import urlparse
import app.clients.bifrost.user as thumbnail
import json
import pytest 

BRAND = 'bluehost'

token = Token.create_test_token(brand=BRAND)
token_data = Token.decode(token)

#TODO: consolidate into function like mock_validate
token_subject = TokenSubject.parse(token_data)
token_data['brand'] = token_subject.brand 

pytestmark = pytest.mark.anyio


class MockUrlObject(str):
    def __init__(self, url):
        self.url = url
        self.path = urlparse(url).path
    def __str__(self):
        return self.url


class MockRequestObject():
    def __init__(self, method='GET', url='', headers=None, query_params={}, path_params={}, body=None, func_name=''):
        body = body or {}
        headers = headers or {}

        if 'Authorization' not in headers:
            headers['Authorization'] = 'bearer mocktoken'

        import types

        self.method = method
        self.headers = Headers(headers)
        self.query_params = QueryParams(query_params)
        self.path_params = path_params
        self.request_body = body
        self.url = MockUrlObject(url)

        async def mock_body():
            return json.dumps(body)

        self.body = mock_body

        async def mock_json():
            body = await self.body()
            return json.loads(body)

        self.json = mock_json

        endpoint = types.SimpleNamespace()
        endpoint.__name__ = func_name
        route = types.SimpleNamespace()
        route.name = func_name

        self.scope = {
            'endpoint': endpoint,
            'route': route
            }

        self.state = types.SimpleNamespace()
        self.state.data = {}

async def mock_validate_is_valid(token, context : Context = None):
    return ValidationResult(True, token_data)


async def mock_validate(monkeypatch, target_id=0):
    async def mock_validation_result(token, context):
        return ValidationResult(
            is_valid_token=True,
            decoded_token=token_data,
            message=''
        )

    monkeypatch.setattr(thumbnail, 'validate', mock_validation_result)


async def mock_validate_bifrost(monkeypatch): 

    async def mock_validate_bifrost_result(context : Context = None):
        return ValidationResult(
            is_valid_token=True,
            decoded_token=token_data,
            message=''        
            )

    monkeypatch.setattr(thumbnail, 'validate', mock_validate_bifrost_result)



async def call_bifrost(monkeypatch, function, site_url='cached', body=None, method='GET'):
    req = await request_bifrost(monkeypatch, func_name=function.__name__, site_url=site_url, body=body, method=method)
    return await function(req)

async def mock_request_bifrost(monkeypatch, func_name='default_func_name', site_url='http://bluehost.com', 
    body=None, method='GET', headers=None, mock_validation=True):

    if mock_validation:
        await mock_validate_bifrost(monkeypatch)


    return MockRequestObject(
        url=f'/v1/thumbnail/get-screenshot',
        path_params={'site_url': site_url},
        func_name=func_name,
        body=body,
        method=method,
        headers=headers
    )

# alias
request_bifrost = mock_validate_bifrost
