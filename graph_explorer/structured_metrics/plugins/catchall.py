from . import Plugin


class CatchallPlugin(Plugin):
    """
    Turns metrics that aren't matched by any other plugin in something a bit more useful (than not having them at all)
    Another way to look at it is.. plugin:catchall is the list of targets you can better organize ;)
    Note that the assigned tags (i.e. source tags) are best guesses.  We can't know for sure!
    (this description goes for all catchall plugins)
    """
    priority = -5

    targets = [
        {
            'match': '^(?P<tosplit>[^=]*)$',
            'target_type': 'unknown',
            'tags': {
                 'unit': 'unknown',
                 'source': 'unknown'
            }
        },
    ]


# vim: ts=4 et sw=4:
