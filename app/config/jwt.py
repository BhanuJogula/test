
from app.config.base import BaseConfig

class JwtConfig(BaseConfig):
    _file = 'jwt.json'
    _conf = {
        "private_key": "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEAzWEPb9Znbq8aJuB/ws2VpaPeGE2v9aJtGy05nVSwiMAfPKXU\nQ5urL/kJtaHMMpvWYpNm6gVERQ9vOJ4wlXp3j2/bXhgEUdIKjM+i9rwJfFwVcILR\nni3UCgHDhwA9hN7MmDePXwSGbx1ne6YIgZXKVU4wlB5Gz+U7DQz6lkHko0SwztaJ\n7X+N/k7WA8WZQLpQfRwDrFFN21jZ81g64g1G/yKDRYKeenSOFBIfYDANSym2Oizs\nf0TxzXzAktZcmzhtxyDbV9xkfIiPFYthIUV4ADGwv4PGA1Szh2k4f2E7gXG/WlE1\n/XGjl2oMvzEspdcOaLd5+oxWO7+jyHsCMUWnUQIDAQABAoIBABHfO1+pEbEhDa6K\nZLPH/hi+7MnCoOhILSRrSBM31nDf/xfg+lqzxi7ThhPHM6THyN0lJJSCxtEXqb8M\njP/E+3iA7F8AygdwtrhQLUc5T74BqV/0Eleod0YzpxctXy0b0kQAubo0A5rRvTqW\nVTEpnsTTnAiXpePbd8sH8Rp4O3Q1kudEDp2I0W7faWckU5M3qWQPGqL9TAtY/aEI\n5VJBfhxBu+PzNl3ejw4CGQDHpQNNfYZ7Ll8GgwHFxJm8e3xbZZ4eGKVh5i/FGmUO\nH/bfFvqxyWoE/DKmaC04ri1g4GlDlUXQEA3S9bmKdIZtj/R5M6QQJ89C2Zoh3AbU\n0TENQpECgYEA/wBRJvq6C9N5L/IMIp1NBQ+pYzmlu3srZEEV8Y8H9D2kk518ooay\nIx40TZ5mEux2etAdZNSZyVRT/ll2dVmOGupXJoR1SnHYmfEDHg2UZjUnkr5cdvoo\ndLa7nxcQQouCDQXn2xWNlYfyB5OLTgMiqQsVAlPcHZeQWE+Wa4WTUi0CgYEAzi79\nEKQP73CwMv6osBJKkYLh398US6Wp5GP+lA6ebAoVeUEWzZ+YuDu01eRp+HEr8gXK\n5t3B006GbLBH7D8RKiuUkZyRuGx8mPqsN4prdDLgop1CJHPvkE4Df4yJ/ZPx08EG\n65ZIWz8Wbeamb5/TI7oGTjNAAXlXGpo1Eqi2tDUCgYEA/njZg1Wofg6+nEsnMw/Z\nAZj8h+nKa0riJX0SIeqDnIg7iZga/bH/aS5GMcNFx9Kz9aFkA/Bpu9FstKGgpkEF\nn/SFngmHZxAvgIhUfRQ+KLUY1cckTRMddkO4/m0sq8u+r7JaC3b5wORWcpsZ5HMa\njqlhgN4hBmLvCEH8MTauqs0CgYB67rM+T8OcjMDRttqXGGDTf4jzNQvhyqWQIjqw\nxkKYwi5pfHB/KzAgcKDygtzYH4oHJIMEwaWGOqSVe0l2x2eRkChl5UdRAYYMpDE4\ncFR/FLKw4jiEiYeFr64QR5gi1Cn0int4zcLYfLX/0uzbUxzNiWWnDJGWD2Xq25TX\nSjadHQKBgHc73UePkCYHYIs2HwP8B+nUQ6YLjdbMDm3aZ45hS2OFQ/+N/PnXi5h4\nrl7hLMvJK0vsHVroEVN61t+DQVnI9x6FzRa6RJaVICnBTgUTVKE28hJTBEqGUZFJ\nR70oKHkzrKnZe1KHgsEEqdCv+5f1LMJfqfb0EKYXmYmxmxkaKiP+\n-----END RSA PRIVATE KEY-----",
        "public_keys": {
            "thumbnail": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzWEPb9Znbq8aJuB/ws2V\npaPeGE2v9aJtGy05nVSwiMAfPKXUQ5urL/kJtaHMMpvWYpNm6gVERQ9vOJ4wlXp3\nj2/bXhgEUdIKjM+i9rwJfFwVcILRni3UCgHDhwA9hN7MmDePXwSGbx1ne6YIgZXK\nVU4wlB5Gz+U7DQz6lkHko0SwztaJ7X+N/k7WA8WZQLpQfRwDrFFN21jZ81g64g1G\n/yKDRYKeenSOFBIfYDANSym2Oizsf0TxzXzAktZcmzhtxyDbV9xkfIiPFYthIUV4\nADGwv4PGA1Szh2k4f2E7gXG/WlE1/XGjl2oMvzEspdcOaLd5+oxWO7+jyHsCMUWn\nUQIDAQAB\n-----END PUBLIC KEY-----",
            "jarvis": ""
        } 
    }
    
    
    def __init__(self, env: str = None, ignore_env_vals: bool = False, auto_load: bool = True):
        super().__init__(env, ignore_env_vals)
        if auto_load:
            self._conf |= super().load(self._file)

    def load(self):
        self._conf |= super().load(self._file)