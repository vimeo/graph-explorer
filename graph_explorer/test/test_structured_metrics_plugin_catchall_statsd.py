from graph_explorer import structured_metrics
import testhelpers


def test_parse_count_and_rate():
    s_metrics = structured_metrics.StructuredMetrics()
    s_metrics.load_plugins()
    tags_base = {
        'n1': 'foo',
        'n2': 'req',
        'plugin': 'catchall_statsd',
        'source': 'statsd',
    }

    def get_proto2(key, target_type, unit, updates={}):
        return testhelpers.get_proto2(key, tags_base, target_type, unit, updates)

    key = "stats.foo.req"
    expected = get_proto2(key, 'rate', 'unknown/s')
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats_counts.foo.req"
    expected = get_proto2(key, 'count', 'unknown')
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
    }

    def get_proto2(key, target_type, unit, updates={}):
        return testhelpers.get_proto2(key, tags_base, target_type, unit, updates)

    key = "stats.timers.memcached_default_get.count"
    expected = get_proto2(key, 'count', 'Pckt')
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.memcached_default_get.count_ps"
    expected = get_proto2(key, 'rate', 'Pckt/s')
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.memcached_default_get.lower"
    expected = get_proto2(key, 'gauge', 'ms', {'type': 'lower'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.memcached_default_get.mean"
    expected = get_proto2(key, 'gauge', 'ms', {'type': 'mean'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.memcached_default_get.mean_90"
    expected = get_proto2(key, 'gauge', 'ms', {'type': 'mean_90'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.memcached_default_get.median"
    expected = get_proto2(key, 'gauge', 'ms', {'type': 'median'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.memcached_default_get.std"
    expected = get_proto2(key, 'gauge', 'ms', {'type': 'std'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.memcached_default_get.sum"
    expected = get_proto2(key, 'gauge', 'ms', {'type': 'sum'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.memcached_default_get.sum_90"
    expected = get_proto2(key, 'gauge', 'ms', {'type': 'sum_90'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.memcached_default_get.upper"
    expected = get_proto2(key, 'gauge', 'ms', {'type': 'upper'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.memcached_default_get.upper_90"
    expected = get_proto2(key, 'gauge', 'ms', {'type': 'upper_90'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.memcached_default_get.histogram.bin_0_01"
    expected = get_proto2(key, 'gauge', 'freq_abs', {'bin_upper': '0.01', 'orig_unit': 'ms'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.memcached_default_get.histogram.bin_5"
    expected = get_proto2(key, 'gauge', 'freq_abs', {'bin_upper': '5', 'orig_unit': 'ms'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.memcached_default_get.histogram.bin_inf"
    expected = get_proto2(key, 'gauge', 'freq_abs', {'bin_upper': 'inf', 'orig_unit': 'ms'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]
