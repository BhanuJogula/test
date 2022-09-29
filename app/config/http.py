
from app.config.base import BaseConfig

class HttpConfig(BaseConfig):
    _file = 'http.json'
    _conf = {
        "cors_origins": "*"
    }
    
    def __init__(self, env: str = None, ignore_env_vals: bool = False, auto_load: bool = True):
        super().__init__(env, ignore_env_vals)
        if auto_load:
            self._conf |= super().load(self._file)

    def load(self):
        self._conf |= super().load(self._file)
