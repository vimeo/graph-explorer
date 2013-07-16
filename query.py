import re


def parse_query(query_str):
    avg_over_match = '^([0-9]*)([sMhdwm])$'
    query = {
        'patterns': [],
        'group_by': ['target_type=', 'what=', 'server'],
        'sum_by': [],
        'avg_over': None
    }

    # for a call like ('foo bar baz quux', 'bar ', 'baz', 'def')
    # returns ('foo quux', 'baz') or the original query and the default val if no match
    def parse_out_value(query_str, predicate_match, value_match, value_default):
        match = re.search('(%s%s)' % (predicate_match, value_match), query_str)
        value = value_default
        if match and match.groups() > 0:
            value = match.groups(1)[0].replace(predicate_match, '')
            query_str = query_str[:match.start(1)] + query_str[match.end(1):]
        return (query_str, value)

    (query_str, query['statement']) = parse_out_value(query_str, '^', '(graph|list) ', 'graph')
    query['statement'] = query['statement'].rstrip()

    (query_str, query['to']) = parse_out_value(query_str, 'to ', '[^ ]+', 'now')
    (query_str, query['from']) = parse_out_value(query_str, 'from ', '[^ ]+', '-24hours')

    (query_str, group_by_str) = parse_out_value(query_str, 'GROUP BY ', '[^ ]+', None)
    (query_str, extra_group_by_str) = parse_out_value(query_str, 'group by ', '[^ ]+', None)
    (query_str, sum_by_str) = parse_out_value(query_str, 'sum by ', '[^ ]+', None)
    (query_str, avg_over_str) = parse_out_value(query_str, 'avg over ', '[^ ]+', None)
    if group_by_str is not None:
        query['group_by'] = group_by_str.split(',')
    elif extra_group_by_str is not None:
        query['group_by'] = [tag for tag in query['group_by'] if tag.endswith('=')]
        query['group_by'].extend(extra_group_by_str.split(','))
    if sum_by_str is not None:
        query['sum_by'] = sum_by_str.split(',')
    if avg_over_str is not None:
        # avg_over_str should be something like 'h', '1m', etc
        avg_over = re.match(avg_over_match, avg_over_str)
        if avg_over is not None:  # if None, that's an invalid request. ignore it. TODO error to user
            avg_over = avg_over.groups()
            query['avg_over'] = (int(avg_over[0]), avg_over[1])
    for tag in query['group_by']:
        if tag.endswith('='):
            query['patterns'].append(tag)

    (query_str, query['limit_targets']) = parse_out_value(query_str, 'limit ', '[^ ]+', 500)

    # split query_str into multiple patterns which are all matched independently
    # this allows you write patterns in any order, and also makes it easy to use negations
    query['patterns'] += query_str.split()
    return query


def normalize_query(query):
    unit_conversions = {
        '/M': [
            ['scale', '60']
        ],
        '/h': [
            ['scale', '3600']
        ],
        '/d': [
            ['scale', str(3600 * 24)]
        ],
        '/w': [
            ['scale', str(3600 * 24 * 7)]
        ],
        '/mo': [
            ['scale', str(3600 * 24 * 30)]
        ]
    }
    target_modifiers = []
    for (i, pattern) in enumerate(query['patterns']):
        if pattern.startswith('unit='):
            unit = pattern.split('=')[1]
            for (divisor, modifiers) in unit_conversions.items():
                if unit.endswith(divisor):
                    unit = "%s/s" % unit[0:-(len(divisor))]
                    query['patterns'][i] = "unit=%s" % unit
                    target_modifiers.extend(modifiers)
                    break
    return (query, target_modifiers)


def parse_patterns(query, graph=False):
    # prepare higher performing query structure, to later match objects
    # note that if you have twice the exact same "word" (ignoring leading '!'), the last one wins
    """
    if query['patterns'] looks like so:
    ['target_type=', 'what=', '!tag_k=not_equals_thistag_v', 'tag_k:match_this_val', 'arbitrary', 'words']

    then the patterns will look like so:
    {
    'tag_k=not_equals_thistag_v': {'negate': True, 'match_tag_equality': ['tag_k', 'not_equals_thistag_v']},
    'target_type=':               {'negate': False, 'match_tag_equality': ['target_type', '']},
    'what=':                      {'negate': False, 'match_tag_equality': ['what', '']},
    'tag_k:match_this_val':       {'negate': False, 'match_tag_regex': ['tag_k', 'match_this_val']},
    'words':                      {'negate': False, 'match_id_regex': <_sre.SRE_Pattern object at 0x2612cb0>},
    'arbitrary':                  {'negate': False, 'match_id_regex': <_sre.SRE_Pattern object at 0x7f6cc000bd90>}
    }
    """
    patterns = {}
    for pattern in query['patterns']:
        negate = False
        if pattern.startswith('!'):
            negate = True
            pattern = pattern[1:]
        patterns[pattern] = {'negate': negate}
        if '=' in pattern:
            if not graph or pattern not in ('target_type=', 'what='):
                patterns[pattern]['match_tag_equality'] = pattern.split('=')
            else:
                del patterns[pattern]
        elif ':' in pattern:
            if not graph or pattern not in ('target_type:', 'what:'):
                patterns[pattern]['match_tag_regex'] = pattern.split(':')
            else:
                del patterns[pattern]
        else:
            patterns[pattern]['match_id_regex'] = re.compile(pattern)
    return patterns
