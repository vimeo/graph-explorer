#!/usr/bin/env python2

"""
Base Plugin class
"""

import re


def camel_to_underscore(name):
    '''
    from http://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-camel-case/1176023#1176023
    '''
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


class Plugin(object):
    priority = 0
    graphs = {}

    def get_graphs(self):
        ret = {}
        for k, v in self.graphs.items():
            v['graph']['tags'] = {'plugin': self.classname_to_tag()}
            ret[k] = v['graph']
        return ret

    @classmethod
    def classname_to_tag(cls):
        '''
        FooBarHTTPPlugin -> foo_bar_http
        '''
        name = cls.__name__.replace('Plugin', '')
        return camel_to_underscore(name)

# vim: ts=4 et sw=4:
