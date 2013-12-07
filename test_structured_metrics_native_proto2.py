import structured_metrics


def test_native_proto2():
    '''
    for now, SM should ignore native proto2 metrics, ie as soon as they contain a space
    assume that we index them straight away with carbon-tagger.
    later we may add a plugin for them too.
    '''
    s_metrics = structured_metrics.StructuredMetrics()
    s_metrics.load_plugins()

    key = "foo.bar=blah.baz"
    real = s_metrics.list_metrics([key])
    assert len(real) == 0
