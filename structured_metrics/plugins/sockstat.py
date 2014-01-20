from . import Plugin


class SockstatPlugin(Plugin):
    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.sockets\.(?P<protocol>tcp|udp)?_?(?P<type>[^\.]+)$',
            'target_type': 'gauge',
            'configure': lambda self, target: self.add_tag(target, 'unit', 'Sock')
        }
    ]

# vim: ts=4 et sw=4:
