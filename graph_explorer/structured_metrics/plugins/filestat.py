from . import Plugin


class FilestatPlugin(Plugin):

    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.files\.(?P<type>assigned|max|unused)$',
            'target_type': 'gauge',
            'tags': {'unit': 'File'}
        },
    ]

# vim: ts=4 et sw=4:
