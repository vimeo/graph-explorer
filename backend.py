#!/usr/bin/env python2
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        raise ImportError("GE requires python2, 2.6 or higher, or 2.5 with simplejson.")
import os
import logging
import pickle
import md5

import config


class MetricsError(Exception):
    def __init__(self, msg, underlying_error):
        self.msg = str(msg)
        self.underlying_error = str(underlying_error)

    def __str__(self):
        return "%s (%s)" % (self.msg, self.underlying_error)


class Backend(object):

    def __init__(self, config, logger=logging):
        self.config = config
        self.logger = logger

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
            metrics = json.load(f)
            # workaround for graphite bug where metrics can have leading dots
            # has been fixed (https://github.com/graphite-project/graphite-web/pull/293)
            # but older graphite versions still do it
            if len(metrics) and metrics[0][0] == '.':
                metrics = [m.lstrip('.') for m in metrics]
            return metrics
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
        self.logger.debug("loading metrics")
        metrics = self.load_metrics()

        self.logger.debug("updating targets")
        targets_all = s_metrics.list_targets(metrics)
        open(config.targets_all_cache_file, 'w').write(pickle.dumps(targets_all))

    def load_data(self):
        self.logger.debug("loading targets")
        targets_all = pickle.loads(open('targets_all.cache').read())
        return targets_all


def get_action_on_rules_match(rules, subject):
    '''
    rules being a a list of tuples, and each tuple having 2 elements, like:
    {'plugin': ['diskspace', 'memory'], 'what': 'bytes'},
    action

    the dict is a list of conditions that must match (and). if the value is an iterable, those count as OR
    action can be whatever you want. the actions for all matching rules are yielded.
    '''
    for (match_rules, action) in rules:
        rule_match = True
        for (tag_k, tag_v) in match_rules.items():
            if tag_k not in subject:
                rule_match = False
                break
            if isinstance(tag_v, basestring):
                if subject[tag_k] != tag_v:
                    rule_match = False
                    break
            else:
                # tag_v is a list -> OR of multiple allowed options
                tag_match = False
                for option in tag_v:
                    if subject[tag_k] == option:
                        tag_match = True
                if not tag_match:
                    rule_match = False
                    break
        if rule_match:
            yield action

# vim: ts=4 et sw=4:
