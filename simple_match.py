import re


# id, data -> an key:object from the dict of objects
# pattern: a pattern structure from match()
def match_pattern(id, data, pattern):
    if 'match_tag_equality' in pattern:
        t_key = pattern['match_tag_equality'][0]
        t_val = pattern['match_tag_equality'][1]
        if len(t_key) is 0 and len(t_val) is 0:
            # this pattern is pointless.
            match_pattern = True
        if len(t_key) > 0 and len(t_val) is 0:
            match_pattern = (t_key in data['tags'])
        if len(t_key) is 0 and len(t_val) > 0:
            match_pattern = False
            for v in data['tags'].values():
                if t_val is v:
                    match_pattern = True
                    break
        if len(t_key) > 0 and len(t_val) > 0:
            match_pattern = (t_key in data['tags'] and data['tags'][t_key] == t_val)
    elif 'match_tag_regex' in pattern:
        t_key = pattern['match_tag_regex'][0]
        t_val = pattern['match_tag_regex'][1]
        if len(t_key) is 0 and len(t_val) is 0:
            # this pattern is pointless.
            match_pattern = True
        if len(t_key) > 0 and len(t_val) is 0:
            match_pattern = False
            for k in data['tags'].iterkeys():
                if re.search(t_key, k) is not None:
                    match_pattern = True
                    break
        if len(t_key) is 0 and len(t_val) > 0:
            match_pattern = False
            for v in data['tags'].values():
                if re.search(t_val, v) is not None:
                    match_pattern = True
                    break
        if len(t_key) > 0 and len(t_val) > 0:
            match_pattern = (t_key in data['tags'] and re.search(t_val, data['tags'][t_key]) is not None)
    else:
        match_pattern = (pattern['match_id_regex'].search(id) is not None)
    return match_pattern


# objects is expected to be a dict with elements like id: data
# id's are matched, and the return value is a dict in the same format
# if you use tags, make sure data['tags'] is a dict of tags or this'll blow up
# if graph, ignores patterns that only apply for targets (tag matching on target_type, what)
def match(objects, patterns, graph=False):
    objects_matching = {}
    for (id, data) in objects.items():
        match_o = True
        for pattern in patterns.values():
            match_p = match_pattern(id, data, pattern)
            if match_p and pattern['negate']:
                match_o = False
            elif not match_p and not pattern['negate']:
                match_o = False
        if match_o:
            objects_matching[id] = data
    return objects_matching
