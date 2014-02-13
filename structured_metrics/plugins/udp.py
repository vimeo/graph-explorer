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
                    'configure': [
                        lambda self, target: self.fix_underscores(target, 'type'),
                        lambda self, target: self.add_tag(target, 'unit', 'Err/s')
                    ]
                },
                {
                    'match': '^servers\.(?P<server>[^\.]+)\.(?P<protocol>udp)\.(?P<type>NoPorts)$',
                    'configure': [
                        lambda self, target: self.add_tag(target, 'unit', 'Event/s'),
                        lambda self, target: self.fix_underscores(target, 'type')
                    ]
                }
            ],
            'target_type': 'rate'
        }
    ]

# vim: ts=4 et sw=4:
