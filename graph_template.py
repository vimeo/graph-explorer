#!/usr/bin/env python2
import re
"""
Graph template
"""
class GraphTemplate:
    """
    Class for graph templates
    """

    def __init__(self):
        self.pattern_object = re.compile(self.pattern)

    def matches (self, metric):
        self.match = self.pattern_object.search(metric)
        if self.match is None:
            return False
        self.name = self.graph_name()
        self.targets = self.graph_targets()
        return self.match

    def graph_build(self):
        return {'title': self.name, 'targets': self.targets}

    def build_graphs (self, metrics):
        """
        For given list of metrics, yield all possible graphs according to our pattern
        """
        graphs = {}
        for metric in metrics:
            if self.matches(metric) and self.name not in graphs:
                graphs[self.name] = self.graph_build()
        return graphs

# vim: ts=4 et sw=4:
