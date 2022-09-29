
from app.config.base import BaseConfig

class LogConfig(BaseConfig):
    _file = 'log.json'
    _conf = {
        "file": "/tmp/thumbnail.log",
        "level": "DEBUG",
        "time_format": "seconds",
        "datadog": {
            "tracing": {
                "https": False,
                "enabled": False,
                "host": "localhost",
                "port": 8126
            },
            "logging": {
                "enabled": False,
                "intake_url": "https://http-intake.logs.datadoghq.com/api/v2/logs"
            }
        }
    }
    
    def __init__(self, env: str = None, ignore_env_vals: bool = False, auto_load: bool = True):
        super().__init__(env, ignore_env_vals)
        if auto_load:
            self._conf |= super().load(self._file)

    def load(self):
        self._conf |= super().load(self._file)