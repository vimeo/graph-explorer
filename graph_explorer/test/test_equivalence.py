from graph_explorer.query import Query
import graph_explorer.graphs as g
from dummyprefs import DummyPrefs


def test_equivalence():
    preferences = DummyPrefs()
    query = Query("")
    query['sum_by'] = {'core': ['']}
    targets = {
        'servers.host.cpu.cpu0.irq': {
            'id': 'servers.host.cpu.cpu0.irq',
            'tags': {
                'core': 'cpu0',
                'plugin': 'cpu',
                'server': 'host',
                'target_type': 'gauge_pct',
                'type': 'irq',
                'unit': 'cpu_state'
            }
        },
        'servers.host.cpu.cpu0.softirq': {
            'id': 'servers.host.cpu.cpu0.softirq',
            'tags': {
                'core': 'cpu0',
                'plugin': 'cpu',
                'server': 'host',
                'target_type': 'gauge_pct',
                'type': 'softirq',
                'unit': 'cpu_state'
            }
        },
        'servers.host.cpu.cpu2.irq': {
            'id': 'servers.host.cpu.cpu2.irq',
            'tags': {
                'core': 'cpu2',
                'plugin': 'cpu',
                'server': 'host',
                'target_type': 'gauge_pct',
                'type': 'irq',
                'unit': 'cpu_state'
            }
        },
        'servers.host.cpu.cpu2.softirq': {
            'id': 'servers.host.cpu.cpu2.softirq',
            'tags': {
                'core': 'cpu2',
                'plugin': 'cpu',
                'server': 'host',
                'target_type': 'gauge_pct',
                'type': 'softirq',
                'unit': 'cpu_state'
            }
        },
        'servers.host.cpu.total.irq': {
            'id': 'servers.host.cpu.total.irq',
            'tags': {
                'core': '_sum_',
                'plugin': 'cpu',
                'server': 'host',
                'target_type': 'gauge_pct',
                'type': 'irq',
                'unit': 'cpu_state'
            }
        },
        'servers.host.cpu.total.softirq': {
            'id': 'servers.host.cpu.total.softirq',
            'tags': {
                'core': '_sum_',
                'plugin': 'cpu',
                'server': 'host',
                'target_type': 'gauge_pct',
                'type': 'softirq',
                'unit': 'cpu_state'
            }
        }
    }

    graphs, _query = g.build_from_targets(targets, query, preferences)
    assert len(graphs) == 1
    _, graph = graphs.popitem()
    assert len(graph['targets']) == 2
    ids = [t['id'] for t in graph['targets']]
    assert ids == ['servers.host.cpu.total.irq', 'servers.host.cpu.total.softirq']

    # if there's a filter, equivalence doesn't hold and we should get 2 targets,
    # each the sum of two non-sums
    # and the _sum_ metrics should be removed
    query = Query("core:(_sum_|cpu0|cpu2) sum by core")
    #query['sum_by'] = {'core': ['']}
    #query['patterns'].append('core:(_sum_|cpu0|cpu2)')
    graphs, _query = g.build_from_targets(targets, query, preferences)
    assert len(graphs) == 1
    _, graph = graphs.popitem()
    assert len(graph['targets']) == 2
    ids = [t['id'] for t in graph['targets']]
    assert ids == [
        ['servers.host.cpu.cpu0.softirq', 'servers.host.cpu.cpu2.softirq'],
        ['servers.host.cpu.cpu0.irq', 'servers.host.cpu.cpu2.irq']
    ]
