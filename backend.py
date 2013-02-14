#!/usr/bin/env python2
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        raise ImportError("GE requires python2, 2.6 or higher, or 2.5 with simplejson.")
import os


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

    def stat_metrics(self):
        try:
            return os.stat(self.config.filename_metrics)
        except OSError, e:
            raise MetricsError("Can't load metrics file", e)

    def update_data(self, s_metrics):
        print "loading metrics"
        metrics = self.load_metrics()
        print "listing targets"
        targets_all = s_metrics.list_targets(metrics)
        print "listing graphs"
        graphs_all = s_metrics.list_graphs(metrics)

        return (metrics, targets_all, graphs_all)

# vim: ts=4 et sw=4:
