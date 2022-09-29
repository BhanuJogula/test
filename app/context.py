import uuid
from fastapi import Request
from app.config import logCfg
from typing import Any
import time

def get_context(request : Request):
    pass

class Context:
    def __init__(self, request : Request):
        self.request = request

    def init(self):
        self.request.state.data = { 'request_id': str(uuid.uuid4()) }

    def get(self):
        return self.request.state.data

    def set(self, key : str, value : Any):
        self.request.state.data[key] = value

    def set_time(self, key : str, start_time : int):
        elapsed = time.time_ns() - start_time

        if logCfg.time_format == 'seconds':
            elapsed = elapsed / 1000000000 
        self.set(key, elapsed)
        