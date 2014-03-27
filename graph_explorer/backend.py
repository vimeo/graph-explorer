#!/usr/bin/env python2
import json
import os
import logging
import urllib2
from urlparse import urljoin


class MetricsError(Exception):
    def __init__(self, msg, underlying_error):
        Exception.__init__(self, msg, underlying_error)
        self.msg = str(msg)
        self.underlying_error = str(underlying_error)

    def __str__(self):
        return "%s (%s)" % (self.msg, self.underlying_error)


class Backend(object):
    def __init__(self, config, logger=logging):
        self.config = config
        self.logger = logger

    def download_metrics_json(self):
        url = urljoin(self.config.graphite_url_server, "metrics/index.json")
        if self.config.graphite_username is not None and self.config.graphite_password is not None:
            username = self.config.graphite_username
            password = self.config.graphite_password
            passmanager = urllib2.HTTPPasswordMgrWithDefaultRealm()
            passmanager.add_password(None, url, username, password)
            authhandler = urllib2.HTTPBasicAuthHandler(passmanager)
            opener = urllib2.build_opener(authhandler)
            urllib2.install_opener(opener)

        response = urllib2.urlopen(url)

        with open('%s.tmp' % self.config.filename_metrics, 'w') as m:
            m.write(response.read())
        try:
            os.unlink(self.config.filename_metrics)
        except OSError:
            pass
        os.rename('%s.tmp' % self.config.filename_metrics, self.config.filename_metrics)

    def load_metrics(self):
        try:
            with open(self.config.filename_metrics, 'r') as f:
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

        self.logger.debug("removing outdated targets")
        s_metrics.remove_metrics_not_in(metrics)

        self.logger.debug("updating targets")
        s_metrics.update_targets(metrics)


def make_config(config):
    # backwards compat.
    if hasattr(config, 'graphite_url'):
        if not hasattr(config, 'graphite_url_server'):
            config.graphite_url_server = config.graphite_url
        if not hasattr(config, 'graphite_url_client'):
            config.graphite_url_client = config.graphite_url
    return config


def get_action_on_rules_match(rules, subject):
    '''
    rules being a a list of tuples, and each tuple having 2 elements, like:
    {'plugin': ['diskspace', 'memory'], 'unit': 'B'},
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
