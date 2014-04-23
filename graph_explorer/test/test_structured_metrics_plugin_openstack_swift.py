from graph_explorer import structured_metrics
import testhelpers


# test openstack_swift timers, but also reusability of statsd timer logic
def test_parse_timers():
    s_metrics = structured_metrics.StructuredMetrics()
    s_metrics.load_plugins()
    tags_base = {
        'server': 'lvimdfsproxy2',
        'plugin': 'openstack_swift',
        'swift_type': 'object',
        'service': 'proxy-server',
        'http_method': 'GET',
        'http_code': '200'
    }

    def get_proto2(key, target_type, unit, updates={}):
        return testhelpers.get_proto2(key, tags_base, target_type, unit, updates)

    key = "stats.timers.lvimdfsproxy2.proxy-server.object.GET.200.timing.count"
    expected = get_proto2(key, 'count', 'Pckt')
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.lvimdfsproxy2.proxy-server.object.GET.200.timing.count_ps"
    expected = get_proto2(key, 'rate', 'Pckt/s')
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.lvimdfsproxy2.proxy-server.object.GET.200.timing.lower"
    expected = get_proto2(key, 'gauge', 'ms', {'stat': 'lower'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.lvimdfsproxy2.proxy-server.object.GET.200.timing.mean"
    expected = get_proto2(key, 'gauge', 'ms', {'stat': 'mean'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.lvimdfsproxy2.proxy-server.object.GET.200.timing.mean_90"
    expected = get_proto2(key, 'gauge', 'ms', {'stat': 'mean_90'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.lvimdfsproxy2.proxy-server.object.GET.200.timing.median"
    expected = get_proto2(key, 'gauge', 'ms', {'stat': 'median'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.lvimdfsproxy2.proxy-server.object.GET.200.timing.std"
    expected = get_proto2(key, 'gauge', 'ms', {'stat': 'std'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.lvimdfsproxy2.proxy-server.object.GET.200.timing.sum"
    expected = get_proto2(key, 'gauge', 'ms', {'stat': 'sum'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.lvimdfsproxy2.proxy-server.object.GET.200.timing.sum_90"
    expected = get_proto2(key, 'gauge', 'ms', {'stat': 'sum_90'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.lvimdfsproxy2.proxy-server.object.GET.200.timing.upper"
    expected = get_proto2(key, 'gauge', 'ms', {'stat': 'upper'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.lvimdfsproxy2.proxy-server.object.GET.200.timing.upper_90"
    expected = get_proto2(key, 'gauge', 'ms', {'stat': 'upper_90'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]
