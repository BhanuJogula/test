from app.logger import log
from app.config import bifrostCfg
from ddtrace import tracer
from hashlib import md5
from inspect import stack, getmodule

import app.init
import httpx
import json
import time


app.init.init()

class ResourceNotFoundError(Exception):
    """Exception type to indicate a resource was not found"""

DEFAULT_TIMEOUT = bifrostCfg.get('timeout', 60)

LOG_TEXT = bifrostCfg.get('log_text', False)
LOG_JSON = bifrostCfg.get('log_json', False)

class HttpLog:
    def log_text(self):
            response_tag = f"\n---------- {self.route_name} ----------"
            log.debug(f"\n{response_tag}\n Bifrost Url:  {self.path}\nRequest:  {json.dumps(self.request_body)}\nResponse: {json.dumps(self.response_body)}\n")

    def get_log_data(self):
        return {
            'http.url' : self.url,
            'http.status_code' : self.status_code,
            'http.request_id' : self.request_id,
            'http.duration' : self.duration,
            'http.details.route_name': self.route_name,
            'http.details.request_body' : self.request_body,
            'http.details.response_body' : self.response_body,
            'http.details.result' : self.result,
            'http.details.duration_seconds': self.duration / 1000000000
        }
    
    def log_json(self):
        log_data = { 'Body': 'Thumbnail Request', 'Attributes': self.get_log_data()}
        log.debug(json.dumps(log_data, indent=4))

    def log(self):
        if LOG_TEXT:
            self.log_text()
        
        if LOG_JSON:
            self.log_json()

class BifrostService:
    def __init__(self, brand='', logging=True, timeout=DEFAULT_TIMEOUT):
        self.logging = logging
        self.timeout = timeout
        
        caller_module = getmodule(stack()[1][0])
        if caller_module and caller_module.__name__.startswith('app.routers'):
            raise Exception("Using ThumnailClient in routes is forbidden")

    @tracer.wrap()
    async def call(self, method, request_body=None, timeout=0) -> dict:
        """Make a call to the Bifrost Service API

        Args:
            method(str): Bifrost method to execute
            request_body(dict): arguments to include in the Bifrost API request body

        Raises:
            Exception: when the Bifrost Service API call returns an 'error' key in the response

        Returns:
            (dict): response body
        """
        request_body = request_body or {}
        base_url = f"https://{bifrostCfg.host}"
        path = f"/{method}"
        secret = self._generate_auth_token(path, request_body)

        force_override = 'false'
        if (request_body["force_override"]):
            force_override = request_body["force_override"]
        headers = {
            "Content-Type": "application/json",
            "x-api-key": bifrostCfg.secret,
            "force-override": force_override
        }

        data_json = json.dumps(request_body)
        request_url = f"{base_url}{path}"

        start_time = time.time_ns()
        timeout = timeout or self.timeout
        print("Request URL: ",request_url)
        with tracer.trace('bifrost', resource=method, service='bifrost'):
            async with httpx.AsyncClient() as client:
                response = await client.post(request_url, content=data_json, headers=headers, timeout=timeout)

        elapsed_time = time.time_ns() - start_time
        response_json = json.loads(response.text)

        if self.logging:
            log_data = HttpLog()
            log_data.url = request_url
            log_data.route_name = method
            log_data.path = path
            log_data.request_body = request_body
            log_data.response_body = response_json
            log_data.duration = elapsed_time
            log_data.status_code = response.status_code
            log_data.request_id = response.headers.get('x-bifrost-track-id', '')
            log_data.result = True # todo set
            log_data.log()

        if "error" in response_json:
            if response_json.get("type", None) == "not_found":
                raise ResourceNotFoundError(response_json["error"])
            raise Exception(response_json["error"])

        return response_json

    @staticmethod
    def _generate_auth_token(req_path, data):
        """Generate a token that can be used to authorized reqeusts to Bifrost"""

        if not bifrostCfg.secret:
            return 'NO_SECRET_SET'

        body_json = json.dumps(data)
        body_hash = md5(body_json.encode("utf-8")).hexdigest()

        secret = bifrostCfg.secret
        timestamp = int(time.time())
        combined = f"{secret}:{timestamp}:{req_path}:{body_hash}"
        encoded = md5(combined.encode("utf-8")).hexdigest() 
        token = f'{encoded}:{timestamp}'

        full_secret = f'app_id=thumbnail {token}'
        return full_secret
