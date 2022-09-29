import jwt
from app.config import jwtCfg
from app.exception import AppException
from app.logger import log
from datetime import datetime, timezone, timedelta
from ddtrace import tracer

AUDIENCES = ['QA', 'dev', 'production', 'beta']

class UnknownKeyAppException(AppException):
    pass


class Token:
    @staticmethod
    def create_test_token(brand="bluehost",  exp_minutes=5259600, kid='thumbnail', private_key=None):
        """Create a token that can be used in test environment to authenticate requests to Thumbnail API.

        Args
            brand(str): brand the account belongs to

        Returns:
            (str): resulting token string
        """
        token_data = {
            'sub': f'urn:jarvis:{brand}',
            'scope': 'user-fe',
            'act': {
                'sub': f'jarvis:{brand}:user:testuser',
                'role': 'admin'
            },
            'aud': 'QA'
        }

        if exp_minutes != 0:
            exp_minutes = timedelta(minutes=exp_minutes) 
            token_data["exp"] = datetime.now(tz=timezone.utc) + exp_minutes
            token_data["iat"] = datetime.now(tz=timezone.utc) 

        headers = { 'kid': kid }
        private_key = private_key or jwtCfg.private_key.replace('\\n', '\n')
        return jwt.encode(token_data, private_key, "RS256", headers=headers)

    @tracer.wrap()
    @staticmethod
    def decode(token_str):
        """Decode a Thumbnail API token and validates it using a public key.

        Args:
            token_str(str): token string to decode

        Returns:
            (dict): decoded token data
        """
        # When a JWKS endpoint is available we can lookup public keys from that instead of the config (using PyJWKClient)

        public_keys = jwtCfg.public_keys
        header = jwt.get_unverified_header(token_str)
        kid: str = header['kid']
        
        if kid not in public_keys:
            raise UnknownKeyAppException(f'unknown jwt key: {kid}', event='Auth.Token.UnknownKey', status_code=401, data={'kid': kid})
        
        key_info = public_keys[kid] 
        key = key_info['key']
        return jwt.decode(token_str, key, "RS256", audience=AUDIENCES)

    @staticmethod
    def decode_unverified(token_str):
        try:
            return jwt.decode(token_str, options={"verify_signature": False})
        except:
            pass
        return None
