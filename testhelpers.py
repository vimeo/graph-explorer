import copy


def get_proto2(key, tags_base, target_type, unit, updates={}):
    metric = {
        'id': key,
        'tags': copy.deepcopy(tags_base),
    }
    metric['tags'].update(updates)
    metric['tags']['target_type'] = target_type
    metric['tags']['unit'] = unit
    return metric
