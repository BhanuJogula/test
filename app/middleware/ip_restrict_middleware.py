import ipaddress
from fastapi import Request 
import os
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import  Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send
import ipaddress

class IpRestrictMiddlware(BaseHTTPMiddleware):
    def __init__( self, app: ASGIApp ):
        super().__init__(app)
        self.allowed_ips = [ipaddress.ip_network(ip.strip()) for ip in os.getenv('ALLOWED_IPS', '').split(',')]

    async def dispatch(self, request: Request, call_next):
        client_ip = ipaddress.ip_address(request.client.host)

        for allowed_ip in self.allowed_ips:
            if client_ip in allowed_ip:
                response = await call_next(request)
                return response

        print(self.allowed_ips)
        print("IP not allowed: " + str(client_ip))
        return Response('', status_code=403)



        