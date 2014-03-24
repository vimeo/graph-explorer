from graph_explorer import structured_metrics


def test_native_proto2_disabled():
    # by default, the plugin ignores them
    s_metrics = structured_metrics.StructuredMetrics()
    s_metrics.load_plugins()

    key = "foo.bar=blah.baz"
    real = s_metrics.list_metrics([key])
    assert len(real) == 0


def test_native_proto2_enabled():
    DummyCfg = type('DummyCfg', (object,), {})
    DummyCfg.process_native_proto2 = True
    s_metrics = structured_metrics.StructuredMetrics(DummyCfg)
    s_metrics.load_plugins()

    key = "foo.bar=blah.baz.target_type=rate.unit=MiB/d"
    real = s_metrics.list_metrics([key])
    assert len(real) == 1
    assert real.values()[0] == {
        'id': key,
        'tags': {
            'n1': 'foo',
            'bar': 'blah',
            'n3': 'baz',
            'target_type': 'rate',
            'unit': 'MiB/d'
        }
    }
