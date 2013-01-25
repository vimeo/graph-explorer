from . import Plugin


class UdpPlugin(Plugin):
    targets = [
        {
            'targets': [
                {
                    'match': '^servers\.(?P<server>[^\.]+)\.(?P<protocol>udp)\.(?P<type>In|Out)(?P<what>Datagrams)$',
                    'configure': lambda self, target: self.fix_underscores(target, ['type', 'what'])
                },
                {
                    'match': '^servers\.(?P<server>[^\.]+)\.(?P<protocol>udp)\.(?P<type>[^\.]+)(?P<what>Errors)$',
                    'configure': lambda self, target: self.fix_underscores(target, ['type', 'what'])
                },
                {
                    'match': '^servers\.(?P<server>[^\.]+)\.(?P<protocol>udp)\.(?P<type>NoPorts)$',
                    'configure': [
                        lambda self, target: self.add_tag(target, 'what', 'udp_events'),
                        lambda self, target: self.fix_underscores(target, 'type')
                    ]
                }
            ],
            'default_group_by': 'server',
            'target_type': 'rate'
        }
    ]

# vim: ts=4 et sw=4:
