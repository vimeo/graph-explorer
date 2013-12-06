from . import Plugin


class FilestatPlugin(Plugin):

    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.files\.(?P<type>assigned|max|unused)$',
            'target_type': 'gauge',
            'configure': lambda self, target: self.add_tag(target, 'what', 'files')
        },
    ]

# vim: ts=4 et sw=4:
