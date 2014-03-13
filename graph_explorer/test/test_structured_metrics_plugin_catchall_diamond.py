import testhelpers
from graph_explorer import structured_metrics


def test_basic():
    s_metrics = structured_metrics.StructuredMetrics()
    s_metrics.load_plugins()
    tags_base = {
        'plugin': 'catchall_diamond',
        'source': 'diamond',
    }

    def get_proto2(key, target_type, unit, updates={}):
        return testhelpers.get_proto2(key, tags_base, target_type, unit, updates)

    key = "servers.web123.foo.bar"
    expected = get_proto2(key, 'unknown', 'unknown', {'server': 'web123', 'n1': 'foo', 'n2': 'bar'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]
