import copy
import structured_metrics


def test_basic():
    s_metrics = structured_metrics.StructuredMetrics()
    s_metrics.load_plugins()
    tags_base = {
        'plugin': 'catchall_diamond',
        'source': 'diamond',
        'target_type': 'unknown',
        'unit': 'unknown'
    }

    def get_proto2(key, updates):
        expected = {
            'id': key,
            'tags': copy.deepcopy(tags_base)
        }
        expected['tags'].update(updates)
        return expected

    key = "servers.web123.foo.bar"
    expected = get_proto2(key, {'server': 'web123', 'n1': 'foo', 'n2': 'bar'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]
