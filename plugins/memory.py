from . import Plugin


class MemoryPlugin(Plugin):
    target_types = {
        'gauge': {
            'match': '^servers\.(?P<server>[^\.]+)\.memory\.(?P<type>.*)$',
            'default_group_by': 'server',
            'default_graph_options': {'vtitle': 'gauges', 'suffixes': 'binary'}
        }
    }

    def generate_targets(self, target_type, match):
        tags = match.groupdict()
        tags.update({'target_type': target_type, 'plugin': self.classname_to_tag()})
        tags['type'] = self.camel_to_underscore(tags['type'])  # SwapCached -> swap_cached
        target = {
            'target': match.string,
            'tags': tags
        }
        target = self.configure_target(target)
        return {self.get_target_id(target): target}

# vim: ts=4 et sw=4:
