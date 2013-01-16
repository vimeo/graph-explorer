from . import Plugin


class MemoryPlugin(Plugin):
    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.memory\.(?P<type>.*)$',
            'default_group_by': 'server',
            'default_graph_options': {'vtitle': 'gauges', 'suffixes': 'binary'},
            'configure': lambda self, match, target: self.fix_underscores(match, target, 'type'),
            'target_type': 'gauge'
        }
    ]

# vim: ts=4 et sw=4:
