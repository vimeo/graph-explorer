#!/usr/bin/env python2
import re
"""
Graph template
"""


class GraphTemplate:
    # color in light resp. dark version
    # better would be just a "base" and programatically compute lighter/darker versions as needed
    colors = {
        'blue': ('#5C9DFF', '#375E99'),
        'yellow': ('#FFFFB2', '#FFFF00'),
        'green': ('#80CC80', '#009900'),
        'brown': ('#694C2E', '#A59482'),
        'red': ('#FF5C33', '#B24024'),
        'purple': ('#FF94FF', '#995999'),
        'turq': ('#75ACAC', '#197575'),
        'orange': ('#FFC266', '#FF9900'),
        'white': '#FFFFFF',
        'black': '#000000'
    }

    """
    Class for graph templates
    set 2 variables:
    * targets. first match wins
    * pattern_graph: similar, but usually more specific to make sure you only yield 1 graph per "thing that you're graphing"
    """

    def __init__(self):
        for (id, config) in self.target_types.items():
            self.target_types[id]['match_object'] = re.compile(config['match'])
        self.pattern_object_graph = re.compile(self.pattern_graph)

    def get_target_id(self, target):
        target_key = ['targets']
        for tag_key in sorted(target['tags'].iterkeys()):  # including the tag key allows to filter out all http things by just writing 'http'
            tag_val = target['tags'][tag_key]
            if tag_val:
                target_key.append('%s:%s' % (tag_key, tag_val))
        return ' '.join(target_key)

    def generate_targets(self, id, match):
        """
        emit one or more targets in a dict like {'targetname': <target spec>}
        note: this function allows to emit multiple targets, but i doubt that will ever be needed
        (only if you need to maintain state across different metric paths)
        the default implementation is super simple and might actually be enough:
        match.string is just the metric, of course you can go crazy and add graphite functions here.
        you can also do different things depending on the target_type id
        the 'targets_' part should get removed once templates don't yield graphs, and merely targets
        """
        tags = match.groupdict()
        tags.update({'target_type': id})
        target = {
            'target': match.string,
            'tags': tags  #.update({'class': self.class_tag})
            # disable this. now part of target_type id to 1)avoid clashes in global list. maybe we should keep this approach and make the global list namespaced, but we'll see
            # when this approach fails.
            # global tags seems useful because templates can invent their own namespaces and potentially override each other (useful?)
            # let's try to find a use case where we don't want 'swift_object_server_count' but want sep class_tag and target_type like 'count', then we can do the namespace thing
            # such usecase could be a feature like group_by, aggregate_by ... would be weird with the current approach
        }
        target = self.configure_target(target)
        return {self.get_target_id(target): target}

    def configure_target(self, target):
        return target

    def generate_graphs(self):
        """
        emit one or more graphs in a dict like {'graphname': <graph dict>}
        """
        return {}

    def list_targets(self, metrics):
        """
        For given list of metrics, list all possible targets according to our pattern
        The return value is as follows: {
            'id (targetstring)' : {
                'targetstring': '<..>',
                'names': { for each tag : a name }, # will be shown in legend. if group_by server, servername will be in title, no need to repeat it here
                'default_group_by': '<default group_by tag>'
            }
        }
        """
        targets = {}
        for metric in metrics:
            for (id, config) in self.target_types.items():
                match = config['match_object'].search(metric)
                if match is not None:
                    targets.update(self.generate_targets(id, match))
                    continue
        return targets

    def list_graphs(self, metrics):
        """
        For given list of metrics, list all possible graphs according to our pattern
        The return value is as follows: {
            'graph-id' : <graph dict, to be merged in with defaults>
        }
        """
        graphs = {}
        for metric in metrics:
            match = self.pattern_object_graph.search(metric)
            if match is not None:
                graphs.update(self.generate_graphs(match))
        return graphs

# vim: ts=4 et sw=4:
