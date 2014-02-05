def test_config_valid():
    import config
    from validation import ConfigValidator

    c = ConfigValidator(obj=config)
    valid = c.validate()
    if not valid:
        from pprint import pprint
        pprint(c.errors)
    assert valid
