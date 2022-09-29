
from app.config.base import BaseConfig

class DatabaseConfig(BaseConfig):
    _file = 'database.json'
    _conf = {
        "host": "127.0.0.1",
        "database": "thumbnailservice",
        "user": "root",
        "password": "Ananya_03"
    }
    
    def __init__(self, env: str = None, ignore_env_vals: bool = False, auto_load: bool = True):
        super().__init__(env, ignore_env_vals)
        if auto_load:
            self._conf |= super().load(self._file)

    def load(self):
        self._conf |= super().load(self._file)