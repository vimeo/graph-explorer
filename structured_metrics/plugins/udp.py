from . import Plugin


class UdpPlugin(Plugin):
    targets = [
        {
            'targets': [
                {
                    'match': '^servers\.(?P<server>[^\.]+)\.(?P<protocol>udp)\.(?P<type>In|Out)(?P<unit>Datagrams)$',
                    'configure': lambda self, target: self.fix_underscores(target, ['type', 'unit'])
                },
                {
                    'match': '^servers\.(?P<server>[^\.]+)\.(?P<protocol>udp)\.(?P<type>[^\.]+)Errors$',
                    'tags': {'unit': 'Err/s'},
                    'configure': lambda self, target: self.fix_underscores(target, 'type'),
                },
                {
                    'match': '^servers\.(?P<server>[^\.]+)\.(?P<protocol>udp)\.(?P<type>NoPorts)$',
                    'tags': {'unit': 'Event/s'},
                    'configure': lambda self, target: self.fix_underscores(target, 'type')
                }
            ],
            'target_type': 'rate'
        }
    ]

# vim: ts=4 et sw=4:
