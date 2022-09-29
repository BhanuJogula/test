import json

with open('pub') as f:
    t = f.read()
    r = json.dumps({
        "public_keys": {
            "test": {
                "key": t
                }}})

    print(r)
            
