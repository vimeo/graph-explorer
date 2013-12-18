from target import Target


def test_agg_key():
    t = Target({
        'variables': {
            'foo': 'bar',
            'target_type': 'rate',
            'region': 'us-east-1'
        }})

    # catchall bucket
    assert t.get_agg_key({'foo': ['']}) == 'foo:__region=us-east-1,target_type=rate'

    # non catchall bucket
    assert t.get_agg_key({'foo': ['ba', ''], 'bar': ['']}) == 'foo:ba__region=us-east-1,target_type=rate'

    struct = {
        'n3': ['bucketmatch1', 'bucketmatch2'],
        'othertag': ['']
    }
    # none of the structs applies
    assert t.get_agg_key(struct) == '__foo=bar,region=us-east-1,target_type=rate'

    struct = {
        'target_type': [''],
        'region': ['us-east', 'us-west', '']
    }
    # one catchall, the other matches
    assert t.get_agg_key(struct) == 'region:us-east,target_type:__foo=bar'
