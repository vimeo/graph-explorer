import testhelpers
from graph_explorer import structured_metrics


def test_simple():
    s_metrics = structured_metrics.StructuredMetrics()
    s_metrics.load_plugins()
    tags_base = {
        'plugin': 'catchall',
        'source': 'unknown',
    }

    def get_proto2(key, target_type, unit, updates={}):
        return testhelpers.get_proto2(key, tags_base, target_type, unit, updates)

    key = "foo.bar"
    expected = get_proto2(key, 'unknown', 'unknown', {'n1': 'foo', 'n2': 'bar'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]
