from query import Query
import copy
import re


def get_default_parsed_query():
    query = copy.deepcopy(Query.default)
    query['compiled_patterns'] = {}
    query = add_pattern(query, 'target_type=', False, 'target_type=', 'match_tag_equality', ['target_type', ''])
    query = add_pattern(query, 'unit=', False, 'unit=', 'match_tag_equality', ['unit', ''])
    return query


def add_pattern(query, pattern, negate, key, check, val):
    query['patterns'].append(pattern)
    query['compiled_patterns'][key] = {
        'negate': negate,
        check: val
    }
    return query


def test_query_basic():
    ref = get_default_parsed_query()
    query = Query("")
    assert query == ref
    query = Query("foo bar")
    ref = get_default_parsed_query()
    ref = add_pattern(ref, 'foo', False, 'foo', 'match_id_regex', re.compile('foo'))
    ref = add_pattern(ref, 'bar', False, 'bar', 'match_id_regex', re.compile('bar'))
    assert query == ref


def test_query_only_statement():
    ref = get_default_parsed_query()
    ref['statement'] = 'list'
    query = Query("list")
    assert query == ref
    query = Query("list ")
    assert query == ref


def test_query_advanced():
    query = Query("octo -20hours unit=b/s memory group by foo avg by barsum by baz")
    ref = get_default_parsed_query()
    ref = add_pattern(ref, 'octo', False, 'octo', 'match_id_regex', re.compile('octo'))
    ref = add_pattern(ref, '-20hours', False, '-20hours', 'match_id_regex', re.compile('-20hours'))
    ref = add_pattern(ref, 'unit=b/s', False, 'unit=b/s', 'match_tag_equality', ['unit', 'b/s'])
    ref = add_pattern(ref, 'memory', False, 'memory', 'match_id_regex', re.compile('memory'))
    ref = add_pattern(ref, 'by', False, 'by', 'match_id_regex', re.compile('by'))
    ref = add_pattern(ref, 'baz', False, 'baz', 'match_id_regex', re.compile('baz'))
    ref['avg_by'] = {'barsum': ['']}
    ref['group_by'] = {'target_type=': [''], 'unit=': [''], 'foo': ['']}
    assert query == ref
    query = Query("stack from -20hours to -10hours avg over 10M sum by foo:bucket1|bucket2,bar min 100 max 200")
    ref = get_default_parsed_query()
    ref['statement'] = 'stack'
    ref['avg_over'] = (10, 'M')
    ref['from'] = '-20hours'
    ref['to'] = '-10hours'
    ref['min'] = '100'
    ref['max'] = '200'
    ref['sum_by'] = {'foo': ['bucket1', 'bucket2'], 'bar': ['']}
    assert query == ref
