#!/usr/bin/env python2
import re
"""
Base Plugin class
"""


class Plugin(object):
    priority = 0
    graphs = {}

    def get_graphs(self):
        ret = {}
        for k, v in self.graphs.items():
            v['graph']['tags'] = {'plugin': self.classname_to_tag()}
            ret[k] = v['graph']
        return ret

    def classname_to_tag(self):
        '''
        FooBarHTTPPlugin -> foo_bar_http
        '''
        name = self.__class__.__name__.replace('Plugin', '')
        return self.camel_to_underscore(name)

    def camel_to_underscore(self, name):
        '''
        from http://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-camel-case/1176023#1176023
        '''
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

# vim: ts=4 et sw=4:
