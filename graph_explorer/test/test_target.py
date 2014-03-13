from graph_explorer.target import Target


def test_agg_key():
    t = Target({
        'variables': {
            'foo': 'bar',
            'target_type': 'rate',
            'region': 'us-east-1'
        }})

    # catchall bucket
    assert t.get_agg_key({'foo': ['']}) == 'agg_id_found:foo:__agg_id_missing:__variables:region=us-east-1,target_type=rate'

    # non catchall bucket
    assert t.get_agg_key({'foo': ['ba', ''], 'bar': ['']}) == 'agg_id_found:foo:ba__agg_id_missing:bar__variables:region=us-east-1,target_type=rate'

    struct = {
        'n3': ['bucketmatch1', 'bucketmatch2'],
        'othertag': ['']
    }
    # none of the structs applies
    assert t.get_agg_key(struct) == 'agg_id_found:__agg_id_missing:n3,othertag__variables:foo=bar,region=us-east-1,target_type=rate'

    struct = {
        'target_type': [''],
        'region': ['us-east', 'us-west', '']
    }
    # one catchall, the other matches
    assert t.get_agg_key(struct) == 'agg_id_found:region:us-east,target_type:__agg_id_missing:__variables:foo=bar'
