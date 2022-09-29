
from app.config.base import BaseConfig

class BifrostConfig(BaseConfig):
    _file = 'bifrost.json'
    _conf = {
        "debug": False,
        "host": "esfwdf90a1.execute-api.us-east-1.amazonaws.com",
        "log_json": False,
        "log_text": False,
        "secret": "00962c09-fdff-4b70-88ea-649b77ff0916"
    }
    
    def __init__(self, env: str = None, ignore_env_vals: bool = False, auto_load: bool = True):
        super().__init__(env, ignore_env_vals)
        if auto_load:
            self._conf |= super().load(self._file)

    def load(self):
        self._conf |= super().load(self._file)