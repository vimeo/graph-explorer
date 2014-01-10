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
    def add_tag(target, key, val):
        '''
        add tag to existing set of tags
        overiddes any tag with the same name
        '''
        target['tags'][key] = val

    @staticmethod
    def autosplit(target, nodes=None):
        '''
        for catchall plugins, automatically sets n1, n2, ... tags
        for those nodes that we don't know what they mean
        '''
        if nodes is None:
            nodes = target['tags']['tosplit'].split('.')
        for n, val in enumerate(nodes):
            # put the remainders in n1, n2, .. tags
            target['tags']['n%d' % (n + 1)] = val
        del target['tags']['tosplit']

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
    def gauge(match):
        return {
            'match': match,
            'target_type': 'gauge'
        }

    @staticmethod
    def count(match):
        return {
            'match': match,
            'target_type': 'count'
        }

    @staticmethod
    def rate(match):
        return {
            'match': match,
            'target_type': 'rate'
        }

    @staticmethod
    def counter(match):
        return {
            'match': match,
            'target_type': 'counter'
        }

    @staticmethod
    def statsd_gauge(match):
        return {
            'match': '^stats.gauges\.%s' % match,
            'target_type': 'gauge'
        }

    @staticmethod
    def statsd_count(match):
        return {
            'match': '^stats_counts\.%s' % match,
            'target_type': 'count'
        }

    @staticmethod
    def statsd_rate(match):
        return {
            'match': '^stats\.%s' % match,
            'target_type': 'rate'
        }

# vim: ts=4 et sw=4:
