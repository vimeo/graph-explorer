from . import Plugin


class TcpPlugin(Plugin):
    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.(?P<protocol>tcp)\.(?P<type>.*)$',
            'target_type': 'rate',
            'tags': {'unit': 'Event'},
            'configure': lambda self, target: self.fix_underscores(target, 'type'),
        }
    ]

    def sanitize(self, target):
        target['tags']['type'] = target['tags']['type'].replace('TCP', '')

# vim: ts=4 et sw=4:
