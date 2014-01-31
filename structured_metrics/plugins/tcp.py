from . import Plugin


class TcpPlugin(Plugin):
    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.(?P<protocol>tcp)\.(?P<type>.*)$',
            'target_type': 'rate',
            'configure': [
                lambda self, target: self.fix_underscores(target, 'type'),
                lambda self, target: self.add_tag(target, 'unit', 'Event'),
            ]
        }
    ]

    def sanitize(self, target):
        target['tags']['type'] = target['tags']['type'].replace('TCP', '')

# vim: ts=4 et sw=4:
