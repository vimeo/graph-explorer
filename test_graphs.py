from query import Query
from app import build_graphs_from_targets
from target import Target


def test_aggregation():
    # note: uneven aggregation: we only want 1 resulting metric,
    query = Query("")
    query['avg_by'] = {'server': ['']}
    query['sum_by'] = {'type': ['']}

    targets = {
        'web1.db': {
            'id': 'web1.db',
            'tags': {
                'server': 'web1',
                'type': 'db',
                'n3': 'foo'
            }
        },
        'web1.php': {
            'id': 'web1.php',
            'tags': {
                'server': 'web1',
                'type': 'php',
                'n3': 'foo'
            }
        },
        'web2.db': {
            'id': 'web2.db',
            'tags': {
                'server': 'web2',
                'type': 'db',
                'n3': 'foo'
            }
        },
        'web2.php': {
            'id': 'web2.php',
            'tags': {
                'server': 'web2',
                'type': 'php',
                'n3': 'foo'
            }
        },
        'web2.memcache': {
            'id': 'web2.memcache',
            'tags': {
                'server': 'web2',
                'type': 'memcache',
                'n3': 'foo'
            }
        }
    }
    from pprint import pprint
    for (k, v) in targets.items():
        v = Target(v)
        v.get_graph_info(group_by={})
        targets[k] = v
    graphs, _query = build_graphs_from_targets(targets, query)
    # TODO: there should be only 1 graph, containing all 5 items
    print "Graphs:"
    for (k, v) in graphs.items():
        print "graph key"
        pprint(k)
        print "val:"
        pprint(v)
    assert {} == graphs
