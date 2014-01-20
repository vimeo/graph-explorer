from . import Plugin


class SwiftTempauthPlugin(Plugin):
    targets = [
        {
            'match': '^stats\.(?P<server>[^\.]+)\.tempauth\.AUTH_\.(?P<type>[^\.]+)$',
            'target_type': 'rate',
            'configure': lambda self, target: self.add_tag(target, 'unit', 'Req/s')
        },
        {
            'match': '^stats_counts\.(?P<server>[^\.]+)\.tempauth\.AUTH_\.(?P<type>[^\.]+)$',
            'target_type': 'count',
            'configure': lambda self, target: self.add_tag(target, 'unit', 'Req')
        }
    ]

# vim: ts=4 et sw=4:
