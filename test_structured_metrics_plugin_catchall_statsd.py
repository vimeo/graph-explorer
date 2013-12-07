import copy
import structured_metrics


def test_parse_count_and_rate():
    s_metrics = structured_metrics.StructuredMetrics()
    s_metrics.load_plugins()
    tags_base = {
        'n1': 'foo',
        'n2': 'req',
        'plugin': 'catchall_statsd',
        'source': 'statsd',
    }

    def get_proto2(key, updates, target_type='gauge'):
        expected = {
            'id': key,
            'tags': copy.deepcopy(tags_base),
            'target_type': target_type
        }
        expected['tags']['target_type'] = target_type
        expected['tags'].update(updates)
        return expected

    key = "stats.foo.req"
    expected = get_proto2(key, {'unit': 'unknown/s'}, 'rate')
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    from pprint import pprint
    pprint(expected)
    pprint(real.values()[0])
    assert expected == real.values()[0]

    key = "stats_counts.foo.req"
    expected = get_proto2(key, {'unit': 'unknown'}, 'count')
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]


def test_parse_timers():
    s_metrics = structured_metrics.StructuredMetrics()
    s_metrics.load_plugins()
    tags_base = {
        'n1': 'memcached_default_get',
        'plugin': 'catchall_statsd',
        'source': 'statsd',
        'unit': 'ms'
    }

    def get_proto2(key, updates, target_type='gauge'):
        expected = {
            'id': key,
            'tags': copy.deepcopy(tags_base),
            'target_type': target_type
        }
        expected['tags']['target_type'] = target_type
        expected['tags'].update(updates)
        return expected

    key = "stats.timers.memcached_default_get.count"
    expected = get_proto2(key, {'unit': 'Pckt'}, 'count')
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.memcached_default_get.count_ps"
    expected = get_proto2(key, {'unit': 'Pckt/s'}, 'rate')
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.memcached_default_get.lower"
    expected = get_proto2(key, {'type': 'lower'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.memcached_default_get.mean"
    expected = get_proto2(key, {'type': 'mean'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.memcached_default_get.mean_90"
    expected = get_proto2(key, {'type': 'mean_90'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.memcached_default_get.median"
    expected = get_proto2(key, {'type': 'median'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.memcached_default_get.std"
    expected = get_proto2(key, {'type': 'std'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.memcached_default_get.sum"
    expected = get_proto2(key, {'type': 'sum'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.memcached_default_get.sum_90"
    expected = get_proto2(key, {'type': 'sum_90'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.memcached_default_get.upper"
    expected = get_proto2(key, {'type': 'upper'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.memcached_default_get.upper_90"
    expected = get_proto2(key, {'type': 'upper_90'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.memcached_default_get.histogram.bin_0_01"
    expected = get_proto2(key, {'bin_upper': '0.01', 'unit': 'freq_abs', 'orig_unit': 'ms'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.memcached_default_get.histogram.bin_5"
    expected = get_proto2(key, {'bin_upper': '5', 'unit': 'freq_abs', 'orig_unit': 'ms'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.memcached_default_get.histogram.bin_inf"
    expected = get_proto2(key, {'bin_upper': 'inf', 'unit': 'freq_abs', 'orig_unit': 'ms'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]
