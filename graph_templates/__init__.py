#!/usr/bin/env python2
import re
from abc import ABCMeta, abstractmethod
"""
Graph template
"""
class GraphTemplate:
    __metaclass__ = ABCMeta
    """
    Class for graph templates
    set 2 variables:
    * pattern: your template can yield targets for any match
    * pattern_graph: similar, but usually more specific to make sure you only yield 1 graph per "thing that you're graphing"
    """

    def __init__(self):
        self.pattern_object = re.compile(self.pattern)
        self.pattern_object_graph = re.compile(self.pattern_graph)

    @abstractmethod
    def generate_targets(self):
        """
        emit one or more targets in a dict like {'targetname': <target spec>}
        note: this function allows to emit multiple targets, but i doubt that will ever be needed
        (only if you need to maintain state across different metric paths)
        """
        raise NotImplementedError('cannot instantiate abstract base class')

    @abstractmethod
    def generate_graphs(self):
        """
        emit one or more graphs in a dict like {'graphname': <graph dict>}
        """
        raise NotImplementedError('cannot instantiate abstract base class')

    def list_targets (self, metrics):
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
            match = self.pattern_object.search(metric)
            if match is not None:
                targets.update(self.generate_targets(match))
        return targets

    def list_graphs (self, metrics):
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
