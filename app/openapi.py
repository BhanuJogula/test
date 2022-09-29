import json
import os
import re
from app.logger import log

build_name = os.getenv('OPENSHIFT_BUILD_NAME', 'default-1')
build_num = build_name.split('-')[-1]

if 'prod' in build_name:
    version = '0.' + build_num + '.0'
elif 'beta' in build_name:
    version = '0.1.0-beta.' + build_num
elif 'alpha' in build_name:
    version = '0.1.0-alpha.' + build_num
elif 'staging' in build_name:
    version = '0.1.0-staging.' + build_num
else:
    version = '0.1.0'

openapi = None

log.info("Combining openapi spec...")

combined_openapi = {
    'openapi': '3.0.0',
    'info': {
        'title': 'Thumbnail API',
        'description': 'Thumbnail API is an API is a Thumbnail Generation Service functionality to a customer-facing Front End such as (Account Manager).',
        'version': version
    },
    "components": {
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }
    },
    'paths': {}
}

cur_dir = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

for subdir, dirs, files in os.walk(os.path.join(cur_dir, "routers")): 
    for file in files:
        if file.endswith(".openapi.json"):
            print("Found openapi file: " + file)
            full_path = os.path.join(subdir, file)
            with open(full_path, 'r') as specfile:
                spec = json.load(specfile)
                for path in spec['paths'].values():
                    for path_def in path.values():
                        path_def['security'] = [ {"bearerAuth": []}] 

                combined_openapi['paths'] = combined_openapi['paths'] | spec['paths']

openapi = combined_openapi

def load():
    #TODO refactor load() calls to grab the openapi attr
    return combined_openapi

def get_route(function) -> dict:
    split = function.split('_')
    func_http_method = split[0]
    operation_id = '_'.join(split[1:])

    for path in openapi["paths"].values():
        for (http_method, path_data) in path.items():
            if http_method == func_http_method and path_data["operationId"] == operation_id:
                return path_data



