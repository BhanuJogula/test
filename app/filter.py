import json


def filter_object(obj, schema):
    result = {}
    for (prop, prop_schema) in schema["properties"].items():
        if prop in obj:
            result[prop] = filter_with_schema(obj[prop], prop_schema, prop=prop)
        else:
            raise Exception(f"Property does not exist in response: property={prop}, response={json.dumps(obj)}")

    return result


def filter_list(obj, schema):
    result = []
    for item in obj:
        result.append(filter_with_schema(item, schema["items"]))

    return result


def py_to_schema_type(obj):
    pytype = type(obj).__name__
    if pytype == "dict":
        return "object"
    elif pytype == "list":
        return "array"
    elif pytype == "str":
        return "string"
    elif pytype == "int":
        return "integer"
    elif pytype == "bool":
        return "boolean"
    elif pytype == "NoneType":
        return "null"
    else:
        return "unknown" 


def filter_with_schema(obj, schema, prop=''):
    schema_type = schema["type"]
    obj_type = py_to_schema_type(obj)

    if schema_type == "string" and obj_type == "null":
        pass
    elif schema_type != obj_type:
        err_msg = f"validation failed. type mismatch: schema_type={schema_type}, val_type={obj_type}, val={json.dumps(obj)}"
        if prop:
            err_msg += f", prop={prop}"

        raise Exception(err_msg)

    if obj_type == "object":
        return filter_object(obj, schema)
    elif obj_type == "array":
        return filter_list(obj, schema)

    if 'enum' in schema and obj not in schema['enum']:
        err_msg = f"Failed json schema validation, value not listed in enum: val={obj}"
        if prop:
            err_msg += f", prop={prop}"
           
        raise Exception(err_msg)

    return obj


class FilterWithSchema:

    def __init__(self, spec):
        self.spec = spec

    def filter_response(self, func_name, response):
        split = func_name.split('_')
        func_http_method = split[0]
        operation_id = '_'.join(split[1:])

        schema = None
        for path in self.spec["paths"].values():
            for (http_method, path_data) in path.items():
                if http_method == func_http_method and path_data["operationId"] == operation_id:
                    schema = path_data["responses"]["200"]["content"]["application/json"]["schema"]

        if schema is None:
            raise Exception("Could not find schema to filter")
        return filter_with_schema(response, schema)
