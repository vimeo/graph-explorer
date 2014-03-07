from . import Plugin


class SockstatPlugin(Plugin):
    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.sockets\.(?P<protocol>tcp|udp)?_?(?P<type>[^\.]+)$',
            'target_type': 'gauge',
            'tags': {'unit': 'Sock'}
        }
    ]

# vim: ts=4 et sw=4:
