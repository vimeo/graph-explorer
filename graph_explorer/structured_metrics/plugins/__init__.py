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
    target_default = {
        # one or more functions allow you to dynamically configure target properties based on
        # the match object. the target will receive updated fields from the returned dict
        'configure': [lambda self, target: self.default_configure_target(target)],
    }
    priority = 0
    targets_found = 0

    # useful configure functions:
    def default_configure_target(self, _target):  # pylint: disable=R0201
        return {}

    @staticmethod
    def fix_underscores(target, keys):
        # SwapCached -> swap_cached
        # keys can be a list of keys or just one key
        try:
            for key in keys:
                target['tags'][key] = camel_to_underscore(target['tags'][key])
        except (TypeError, KeyError):
            target['tags'][keys] = camel_to_underscore(target['tags'][keys])

    @staticmethod
    def parse_statsd_timer(target):
        # see if we can get info from the end of the metric string
        nodes = target['tags']['tosplit'].split('.')
        target['tags']['target_type'] = 'gauge'
        if len(nodes) > 1 and nodes[-1].startswith('bin_') and nodes[-2] == 'histogram':
            # graphite uses '.' as node delimiters, so decimal numbers use '_' instead of '.'
            target['tags']['bin_upper'] = nodes[-1].replace('bin_', '').replace('_', '.', 1)
            target['tags']['unit'] = 'freq_abs'
            target['tags']['orig_unit'] = 'ms'
            nodes = nodes[:-2]
        # this is a workaround for buggy metric names like "stats.timers.foo.bar.histogram.bin_0.5"
        # i.e. where the decimal '.' is not replaced by a '_'
        elif len(nodes) > 2 and nodes[-2].startswith('bin_') and nodes[-3] == 'histogram':
            target['tags']['bin_upper'] = "%s.%s" % (nodes[-2].replace('bin_', ''), nodes[-1])
            target['tags']['unit'] = 'freq_abs'
            target['tags']['orig_unit'] = 'ms'
            nodes = nodes[:-3]
        elif len(nodes) > 0:
            if nodes[-1] in ('lower', 'mean', 'mean_90', 'median', 'std', 'sum', 'sum_90', 'upper', 'upper_90'):
                target['tags']['stat'] = nodes[-1]
                target['tags']['unit'] = 'ms'
                nodes = nodes[:-1]
            elif nodes[-1] == 'count_ps':
                target['tags']['target_type'] = 'rate'
                target['tags']['unit'] = 'Pckt/s'
                nodes = nodes[:-1]
            elif nodes[-1] == 'count':
                target['tags']['target_type'] = 'count'
                target['tags']['unit'] = 'Pckt'
                nodes = nodes[:-1]
        if nodes:
            target['tags']['tosplit'] = '.'.join(nodes)
        else:
            del target['tags']['tosplit']

    @staticmethod
    def autosplit(target):
        '''
        for catchall plugins, automatically sets n1, n2, ... tags
        for those nodes that we don't know what they mean
        '''
        if 'tosplit' not in target['tags']:
            return target
        nodes = target['tags']['tosplit'].split('.')
        for n, val in enumerate(nodes):
            # put the remainders in n1, n2, .. tags
            target['tags']['n%d' % (n + 1)] = val
        del target['tags']['tosplit']
        return target

    def get_targets(self):
        # "denormalize" dense configuration list into a new list of full-blown configs
        pre_merge_targets = []
        for target in self.targets:
            if 'targets' in target:
                for sub_target in target['targets']:
                    t = target.copy()
                    del t['targets']
                    t.update(sub_target)
                    pre_merge_targets.append(t)
            else:
                pre_merge_targets.append(target)

        targets = []
        for pre_merge_target in pre_merge_targets:
            # merge options into defaults
            # 'configure' is a special case.. we append new entries to the
            # original list.  this allows you to add extra functions, while
            # maintaining the original (which can be overridden).
            # or don't bother with specifying any configure options, and just
            # override the function.
            target = self.target_default.copy()
            target.update(pre_merge_target)
            target['configure'] = list(self.target_default['configure'])
            if 'configure' in pre_merge_target:
                if not isinstance(pre_merge_target['configure'], (list, tuple)):
                    pre_merge_target['configure'] = [pre_merge_target['configure']]
                target['configure'].extend(pre_merge_target['configure'])
            # compile fast match objects
            # because sometimes a target covers multiple metric naming
            # patterns, we must support a list of possible matching regexes.
            # we can't just do '|'.join(list of regexes)
            # because then we can't repeat group names.
            if isinstance(pre_merge_target['match'], basestring):
                pre_merge_target['match'] = [pre_merge_target['match']]
            target['match_object'] = []
            for regex in pre_merge_target['match']:
                # can raise sre_constants.error ! and maybe other regex errors.
                target['match_object'].append(re.compile(regex))
            # similar for 'no_match' if specified
            if 'no_match' in pre_merge_target:
                if isinstance(pre_merge_target['no_match'], basestring):
                    pre_merge_target['no_match'] = [pre_merge_target['no_match']]
                target['no_match_object'] = []
                for regex in pre_merge_target['no_match']:
                    target['no_match_object'].append(re.compile(regex))
            targets.append(target)

        return targets

    def __init__(self, config=None):
        self.targets = self.get_targets()
        self.config = config

    @staticmethod
    def get_target_id(target):
        target_key = ['targets']
        # including the tag key allows to filter out all http things by just writing 'http'
        for tag_key, tag_val in sorted(target['tags'].items()):
            if tag_val:
                target_key.append('%s:%s' % (tag_key, tag_val))
        return ' '.join(target_key)

    @classmethod
    def __create_target(cls, match, target_config):
        tags = match.groupdict()
        if 'tags' in target_config:
            tags.update(target_config['tags'])
        tags['plugin'] = cls.classname_to_tag()
        try:
            tags['target_type'] = target_config['target_type']
        except:
            pass
        target = {
            'id': match.string,  # graphite metric
            'config': target_config,
            'tags': tags,
        }
        return target

    def __sanitize_target(self, target):
        ret = self.sanitize(target)
        if ret is None:
            return target
        return ret

    def __configure_target(self, target):
        # from dict returned, merge in all keys (not deep. overrides existing
        # keys). you can easily mimic deep merge by just taking original value,
        # merging your stuff in, and returning that, or since modifying the
        # original value directly suffices, just return nothing
        for configure_fn in target['config']['configure']:
            out = configure_fn(self, target)
            if out is not None:
                target.update(out)
        return target

    def __finish_target(self, target):
        # this deals with any 'tosplit' tags left in target['tags']
        # it's important we do this at the end, so that configure functions like
        # parse_statsd_timer had their chance to do things based on what's in
        # autosplit, assign some tags, and provide a modified tosplit set.
        return self.autosplit(target)

    def sanitize(self, _target):  # pylint: disable=R0201
        return None

    def upgrade_metric(self, metric):
        """
        For given proto1 metric, try to upgrade it to proto2 if we can match it to a config
        yield a tuple of id and proto2 metric, being:
            {
                'id': '<..>',  # the exact graphite metric id
                'tags': { tag_key: tag_value [,...]}
            }
        }
        """
        # for every target config, see if the metric meets all criteria
        for target in self.targets:
            # metric must not match any of the no_match objects
            yield_metric = True
            for no_match_object in target.get('no_match_object', []):
                no_match = no_match_object.search(metric)
                if no_match is not None:
                    yield_metric = False
                    break
            if not yield_metric:
                continue
            # first match object that creates a match is a winner, yield it
            for match_object in target['match_object']:
                match = match_object.search(metric)
                if match is not None:
                    target = self.__create_target(match, target)
                    target = self.__sanitize_target(target)
                    target = self.__configure_target(target)
                    target = self.__finish_target(target)
                    del target['config']  # not needed beyond this point
                    self.targets_found += 1
                    return (self.get_target_id(target), target)
        return None

    @classmethod
    def classname_to_tag(cls):
        '''
        FooBarHTTPPlugin -> foo_bar_http
        '''
        name = cls.__name__.replace('Plugin', '')
        return camel_to_underscore(name)

    # experimental shortcut functions to easily define targets.
    # some of these would be better provided by the plugins themselves
    @staticmethod
    def gauge(match, tags={}):
        return {
            'match': match,
            'target_type': 'gauge',
            'tags': tags
        }

    @staticmethod
    def count(match, tags={}):
        return {
            'match': match,
            'target_type': 'count',
            'tags': tags
        }

    @staticmethod
    def rate(match, tags={}):
        return {
            'match': match,
            'target_type': 'rate',
            'tags': tags
        }

    @staticmethod
    def counter(match, tags={}):
        return {
            'match': match,
            'target_type': 'counter',
            'tags': tags
        }

    @staticmethod
    def statsd_gauge(match, tags={}):
        return {
            'match': '^stats.gauges\.%s' % match,
            'target_type': 'gauge',
            'tags': tags
        }

    @staticmethod
    def statsd_count(match, tags={}):
        return {
            'match': '^stats_counts\.%s' % match,
            'target_type': 'count',
            'tags': tags
        }

    @staticmethod
    def statsd_rate(match, tags={}):
        return {
            'match': '^stats\.%s' % match,
            'target_type': 'rate',
            'tags': tags
        }

# vim: ts=4 et sw=4:
