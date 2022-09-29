from cmath import log
from app.context import Context
from app.logger import get_dd_logger
from app.logging.redact import redact
from ddtrace import tracer
from fastapi import Request 
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp
from ..config import logCfg
from socket import gethostname
import datetime
import json
import jwt
import time
import traceback

from app.exception import AppException


class LoggerMiddleware(BaseHTTPMiddleware):
    def __init__( self, app: ASGIApp, debug_headers=False, pretty_json=False):
        # set univseral fields based on app info (pod, build#, etc)
        super().__init__(app)

        self.debug_headers = debug_headers
        self.pretty_json = pretty_json

    def log(self, context_data: dict, hostname):
            # skips logging health-check which floods logs
            if not hostname.startswith('10.'):
                if self.pretty_json:
                    log_json = json.dumps(context_data, indent=4, sort_keys=True)
                else:
                    log_json = json.dumps(context_data, sort_keys=True)

                log_json = redact(log_json)
                if logCfg.env() == 'dev':
                    print(json.dumps(json.loads(log_json), indent=4, sort_keys=True))
                else:
                    print(log_json)
                get_dd_logger(__name__).info(log_json)

    async def dispatch(self, request: Request, call_next):
        start_time = time.time_ns()
        context = Context(request)
        context.init()
        context.set('level', 'info')
        context.set('message', 'http_request_log')
        context.set('timestamp', round(time.time() * 1000))
        context.set('service', 'thumbnail')
        context.set('env', logCfg.env())
        context.set('hostname', gethostname())
        context.set('http.method', request.method)
        context.set('http.url', str(request.url))
        context.set('http.referer', request.headers.get('referer', ''))
        context.set('http.useragent', request.headers.get('user-agent', ''))
        context.set('http.url_details.host', request.url.hostname)
        context.set('http.url_details.path', request.url.path)
        context.set('http.details.origin', request.headers.get('origin' , ''))
        context.set('network.client.ip', request.client.host)

        ip_country = request.headers.get('cf-ipcountry', None) 
        if ip_country is not None:
            context.set('network.client.geoip.country.iso_code', ip_country)

        if request.query_params:
            context.set('http.url_details.queryString', str(request.query_params))

        if self.debug_headers:
            header_dict = {}
            for (k, v) in request.headers.items():
                header_dict[k] = v

            context.set('http.debug.headers', header_dict)

        try:
            span = tracer.current_span()
            if span:
                correlation_ids = (span.trace_id, span.span_id) if span else (None, None)
                if correlation_ids[0] and correlation_ids[1]:
                    context.set('dd.trace_id', correlation_ids[0])
                    context.set('dd.span_id', correlation_ids[1])
            response = await call_next(request)
            context.set('http.status_code', response.status_code)
            return response
        except AppException as e:
            tb = traceback.format_exc()

            if logCfg.env() == 'dev':
                print(tb)

            outer_exception = None
            if type(e.exception) is AppException:
                # if an app exception is wrapped, we just want the inner exception which will be more specific to the problem
                # the original exception is preserved for additional log data
                outer_exception = e
                e = e.exception

            exception_class = type(e.exception).__name__
            if exception_class == "NoneType":
                exception_class = "None"
            
            exception_module = type(e.exception).__module__
            if exception_class == "None":
                exception_module = "None"
            

            kind = e.event
            if e.exception:
                kind += "_" + exception_class

            message = e.event
            
            if e.exception:
                message += f' - {exception_class} - {str(e.exception)}'

            if str(e):
                message += " - " + str(e)

            context.set('level', 'error')
            context.set('error.message', message)
            context.set('error.class', 'App')
            context.set('error.event', e.event)
            context.set('error.kind', kind)
            context.set('error.exception', exception_class)
            context.set('error.data', e.data)
            context.set('error.exception_module', exception_module)
            context.set('error.raw_message', str(e.exception))
            context.set('error.stack', tb)
            
            if outer_exception:
                context.set('error.outer_event', outer_exception.event)
            
            context.set('http.status_code', e.status_code) #default=512

            response_message = json.dumps({'error': e.customer_message})
            
            return Response(content=response_message, status_code=e.status_code)

        except Exception as e:
            tb = traceback.format_exc()

            if logCfg.env() == 'dev':
                print(tb)

            exception_class = type(e).__name__
            if exception_class == "NoneType":
                exception_class = "None"

            event = 'None' 
            kind = f'{event}_{exception_class}'
            message = f'{event} - {exception_class} - {str(e)}'
            
            context.set('level', 'error')
            context.set('error.class', 'Exception')
            context.set('error.message', message)
            context.set('error.event', event)
            context.set('error.kind', kind)
            context.set('error.exception', exception_class),
            context.set('error.exception_module', type(e).__module__)
            context.set('http.status_code', 500)
            context.set('error.stack', tb)

            response_message = json.dumps({'error': 'an error occurred'})
            return Response(content=response_message,status_code=500)
        finally:
            duration = time.time_ns() - start_time

            context.set('duration', duration)
            context.set('duration_seconds', duration / 1_000_000_000)
            # some extra formatting for humans reading raw logs
            context.set('formatted.timestamp', str(datetime.datetime.now()))

            context_data = context.get()
            self.log(context_data, request.url.hostname)

