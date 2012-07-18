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

    def build_graphs (self, metrics):
        """
        For given list of metrics, yield all possible graphs according to our pattern
        """
        graphs = {}
        for metric in metrics:
            match = self.pattern_object.search(metric)
            if match is not None:
                name = self.graph_name(match)
                if name not in graphs:
                    graphs[name] = self.graph_build(name)
        return graphs

# vim: ts=4 et sw=4:
