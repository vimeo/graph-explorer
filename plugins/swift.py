from . import Plugin


class SwiftPlugin(Plugin):

    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.openstackswift\.(?P<category>container_metrics)\.(?P<account>[^\.]+)\.(?P<container>[^\.]+)\.(?P<type>[^\.]+)$',
            'default_group_by': 'type',
            'target_type': 'count',
            'configure': lambda self, match, target: {'target': 'keepLastValue(%s)' % match.string}
        },
        {
            'match': '^servers\.(?P<server>[^\.]+)\.openstackswift\.(?P<category>dispersion)\.?(?P<swift_type>container|object)?\.(?P<type>[^\.]+)$',
            'default_group_by': 'server',
            'default_graph_options': {'vtitle': 'events'},
            'target_type': 'count',
            'configure': lambda self, match, target: {'target': 'keepLastValue(%s)' % match.string}
        }
    ]

# vim: ts=4 et sw=4:
