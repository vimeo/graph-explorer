from graph_explorer import structured_metrics


def test_load():
    s_metrics = structured_metrics.StructuredMetrics()
    errors = s_metrics.load_plugins()
    assert len(errors) == 0
