#!/usr/bin/env python2
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        raise ImportError("GE requires python2, 2.6 or higher, or 2.5 with simplejson.")
import os


class Backend(object):

    def __init__(self, config):
        self.config = config

    def load_metrics(self):
        f = open(self.config.filename_metrics, 'r')
        return json.load(f)

    def stat_metrics(self):
        return os.stat(self.config.filename_metrics)

# vim: ts=4 et sw=4:
