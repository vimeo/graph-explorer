def test_config_valid():
    # TODO update this for new text files
    from graph_explorer import config
    from graph_explorer.validation import ConfigValidator

    c = ConfigValidator(obj=config)
    valid = c.validate()
    if not valid:
        from pprint import pprint
        pprint(c.errors)
    # assert valid
