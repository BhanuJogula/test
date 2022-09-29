import re
import json

# values should be all lower case
default_redacted_keys = [
    'authorization',
    'secret_',
    'api_key'
]

def redact(obj, redacted_keys=default_redacted_keys):
    try:
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, dict):
                    obj[k] = redact(v, redacted_keys)
                else:
                    for rk in redacted_keys:
                        if rk in k.lower():
                            obj[k] = 'REDACTED'
                            break
        elif isinstance(obj, str):
            try:
                obj = json.loads(obj)
                if isinstance(obj, dict):
                    obj = json.dumps(redact(obj, redacted_keys))
            except:
                pass
    except:
        pass
    
    return obj