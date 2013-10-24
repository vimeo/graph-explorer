from query import parse_query
import copy

default_parsed_query = {
    'from': '-24hours',
    'to': 'now',
    'min': None,
    'max': None,
    'avg_by': {},
    'limit_targets': 500,
    'avg_over': None,
    'patterns': ['target_type=', 'unit='],
    'group_by': ['target_type=', 'unit=', 'server'],
    'sum_by': {},
    'statement': 'graph'
}


def test_query_basic():
    query = parse_query("")
    assert query == default_parsed_query
    query = parse_query("foo bar")
    new = copy.deepcopy(default_parsed_query)
    new['patterns'].extend(['foo', 'bar'])
    assert query == new


def test_query_advanced():
    query = parse_query("octo -20hours unit=b/s memory group by foo avg by barsum by baz")
    new = copy.deepcopy(default_parsed_query)
    new['patterns'].extend(['octo', '-20hours', 'unit=b/s', 'memory', 'by', 'baz'])
    new['avg_by'] = {'barsum': ['']}
    new['group_by'] = ['target_type=', 'unit=', 'foo']
    assert query == new
    query = parse_query("stack from -20hours to -10hours avg over 10M sum by foo:bucket1|bucket2,bar min 100 max 200")
    new = copy.deepcopy(default_parsed_query)
    new['statement'] = 'stack'
    new['avg_over'] = (10, 'M')
    new['from'] = '-20hours'
    new['to'] = '-10hours'
    new['min'] = '100'
    new['max'] = '200'
    new['sum_by'] = {'foo': ['bucket1', 'bucket2'], 'bar': ['']}
    assert query == new
