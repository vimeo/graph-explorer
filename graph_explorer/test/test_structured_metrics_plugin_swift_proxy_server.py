from graph_explorer import structured_metrics
import testhelpers


# test swift_proxy_server timers, but also reusability of statsd timer logic
def test_parse_timers():
    s_metrics = structured_metrics.StructuredMetrics()
    s_metrics.load_plugins()
    tags_base = {
        'server': 'lvimdfsproxy2',
        'plugin': 'swift_proxy_server',
        'swift_type': 'object',
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
    expected = get_proto2(key, 'gauge', 'ms', {'type': 'lower'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.lvimdfsproxy2.proxy-server.object.GET.200.timing.mean"
    expected = get_proto2(key, 'gauge', 'ms', {'type': 'mean'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.lvimdfsproxy2.proxy-server.object.GET.200.timing.mean_90"
    expected = get_proto2(key, 'gauge', 'ms', {'type': 'mean_90'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.lvimdfsproxy2.proxy-server.object.GET.200.timing.median"
    expected = get_proto2(key, 'gauge', 'ms', {'type': 'median'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.lvimdfsproxy2.proxy-server.object.GET.200.timing.std"
    expected = get_proto2(key, 'gauge', 'ms', {'type': 'std'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.lvimdfsproxy2.proxy-server.object.GET.200.timing.sum"
    expected = get_proto2(key, 'gauge', 'ms', {'type': 'sum'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.lvimdfsproxy2.proxy-server.object.GET.200.timing.sum_90"
    expected = get_proto2(key, 'gauge', 'ms', {'type': 'sum_90'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.lvimdfsproxy2.proxy-server.object.GET.200.timing.upper"
    expected = get_proto2(key, 'gauge', 'ms', {'type': 'upper'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]

    key = "stats.timers.lvimdfsproxy2.proxy-server.object.GET.200.timing.upper_90"
    expected = get_proto2(key, 'gauge', 'ms', {'type': 'upper_90'})
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert expected == real.values()[0]
