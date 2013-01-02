from . import Plugin


class MemoryPlugin(Plugin):
    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.memory\.(?P<type>.*)$',
            'default_group_by': 'server',
            'default_graph_options': {'vtitle': 'gauges', 'suffixes': 'binary'},
            'configure': lambda self, match, target: self.fix_underscores(match, target),
            'target_type': 'gauge'
        }
    ]

    def fix_underscores(self, match, target):
        # SwapCached -> swap_cached
        target['tags']['type'] = self.camel_to_underscore(target['tags']['type'])
        return {'tags': target['tags']}

# vim: ts=4 et sw=4:
