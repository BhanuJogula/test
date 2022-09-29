
def merge_dicts(dict_a, dict_b, ignore_diff = True, path = None):
    "merges dict_b into dict_a"
    if path is None: path = []
    for key in dict_b:
        if key in dict_a:
            if isinstance(dict_a[key], dict) and isinstance(dict_b[key], dict):
                merge_dicts(dict_a[key], dict_b[key], ignore_diff, path + [str(key)])
            elif dict_a[key] == dict_b[key]:
                pass
            else:
                if ignore_diff:
                    dict_a[key] = dict_b[key]
                else:
                    raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            dict_a[key] = dict_b[key]
    return dict_a
