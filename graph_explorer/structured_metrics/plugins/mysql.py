from . import Plugin


class MysqlPlugin(Plugin):
    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.mysql\.(?P<unit>Thread)s_(?P<type>[^\.]+)$',
            'target_type': 'gauge',
        },
        {
            'match': '^servers\.(?P<server>[^\.]+)\.mysql\.(?P<unit>Conn)ections$',
            'target_type': 'gauge',
        }
    ]

# vim: ts=4 et sw=4:
