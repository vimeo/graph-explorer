#!/usr/bin/env python2
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        raise ImportError("GE requires python2, 2.6 or higher, or 2.5 with simplejson.")
import os
import re
import logging


class MetricsError(Exception):
    def __init__(self, msg, underlying_error):
        self.msg = str(msg)
        self.underlying_error = str(underlying_error)

    def __str__(self):
        return "%s (%s)" % (self.msg, self.underlying_error)


class Backend(object):

    def __init__(self, config):
        self.config = config

    def download_metrics_json(self):
        import urllib2
        response = urllib2.urlopen("%s/metrics/index.json" % self.config.graphite_url)
        m = open('%s.tmp' % self.config.filename_metrics, 'w')
        m.write(response.read())
        m.close()
        os.rename('%s.tmp' % self.config.filename_metrics, self.config.filename_metrics)

    def load_metrics(self):
        try:
            f = open(self.config.filename_metrics, 'r')
            return json.load(f)
        except IOError, e:
            raise MetricsError("Can't load metrics file", e)
        except ValueError, e:
            raise MetricsError("Can't parse metrics file", e)

    # yields metrics that match at least one of the specified patterns
    def yield_metrics(self, match):
        match_objects = [re.compile(regex) for regex in match]
        metrics = self.load_metrics()
        for metric in metrics:
            for m_o in match_objects:
                match = m_o.search(metric)
                if match is not None:
                    yield metric
                    break

    def stat_metrics(self):
        try:
            return os.stat(self.config.filename_metrics)
        except OSError, e:
            raise MetricsError("Can't load metrics file", e)

    def update_data(self, s_metrics):
        logging.debug("loading metrics")
        metrics = self.load_metrics()
        logging.debug("listing targets")
        targets_all = s_metrics.list_targets(metrics)
        logging.debug("listing graphs")
        graphs_all = s_metrics.list_graphs(metrics)

        return (metrics, targets_all, graphs_all)

# vim: ts=4 et sw=4:
