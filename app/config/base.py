import json
import sys
from os import path, environ
from typing import Any
from ..helpers import merge_dicts

class BaseConfig:
    _env: str = None
    _envs: list = ['dev', 'beta', 'prod']
    _conf: dict = {}
    _env_vals: bool = True
     
    def __init__(self, env: str = 'dev', ignore_env_vals: bool = False):
        if env in self._envs:
            self._env = env
        elif ignore_env_vals == False:
            if 'NF_ENV' in environ and environ['NF_ENV'] in self._envs:
                self._env = 'beta'
        self._env_vals = not ignore_env_vals
    
    def __str__(self):
        return f"{json.dumps(self._conf, indent=4)}"
    
    def __getitem__(self, key):
        env_key = f"{self.__env_prefix()}_{key.upper()}"
        if self._env_vals and env_key in environ:
            return json.loads(environ[env_key])
        if key in self._conf:
            return self._conf[key]
        return None
    
    def __env_val(self, key, default=None):
        env_key = f"{self.__env_prefix()}_{key.upper()}"
        if self._env_vals and env_key in environ:
            try:
                return json.loads(environ[env_key])
            except Exception as e:
                return environ[env_key]
        return default
    
    def __set_props(self, props):
        if type(self).__name__ == 'BaseConfig':
            raise Exception("Can't set properties on a BaseConfig")
        for key, val in props.items():
            setattr(self, key, self.__env_val(key, val))

    def env(self):
        if self._env is not None:
            return self._env

        env_val = 'beta'
        if env_val is not None:
            if env_val not in self._envs:
                raise ValueError(f"Invalid environment ({env_val}) must be one of {self._envs}")
            return env_val            
        
        raise EnvironmentError("Couldn't determine environment!")

    def __env_prefix(self):
        return f"{type(self).__name__.replace('Config', '').upper()}"

    def __overrides(self):
        cls_key = type(self).__name__.replace('Config', '').lower()
        if cls_key != 'base':
            or_path = f"{self.dir()}/overrides.json"
            if path.exists(or_path):
                with open(or_path) as conf:
                    cfg = json.load(conf)
                    if type(cfg) != dict:
                        raise ValueError("overrides.json root type must be dict")
                    if cls_key in cfg.keys():
                        return cfg[cls_key]
        return {}

    def dir(self):
        api_root = path.dirname(path.realpath(__file__))
        return path.abspath(f"{api_root}/../../config/{self.env()}")

    def load(self, file: str):
        # Set default config class key + values (self._conf)
        # as properties on the class very first. This makes sure
        # the confiig class gets properties for keys that are not
        # explicitlty defined in the json config / overrides file.
        self.__set_props(self._conf)
        # Next, read the config json file if the file exists.
        cfg_path = f"{self.dir()}/{file}"
        cfg_ret = {}
        if path.exists(cfg_path):
            with open(cfg_path) as conf:
                cfg = json.load(conf)
                if type(cfg) == dict:
                    cfg_ret = cfg
        # Otherwise, assign the default config to cfg_ret.
        else:
            cfg_ret = self._conf
        # Grab any configuration from the overrides.json file
        # and merge it into the return config.
        merge_dicts(cfg_ret, self.__overrides())
        # Set config class properties with keys + values
        # specified in the json file.
        self.__set_props(cfg_ret)
        return cfg_ret

    def get(self, key: str, default: Any = None):
        if self._env_vals:
            env_val = self.__env_val(key)
            if env_val is not None:
                return env_val
        if key in self._conf:
            return self._conf[key]
        else:
            return default
