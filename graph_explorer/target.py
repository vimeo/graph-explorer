import re


class Target(dict):
    def __init__(self, src_dict):
        dict.__init__(self)
        self['match_buckets'] = {}
        self.update(src_dict)

    # targets that can get aggregated together with other tags, must
    # have at least 1 of the aggregation tags ('sum by' / 'avg by')
    # tags in the variables list.
    # targets that can get aggregated together must:
    # * have the same aggregation tag keys (not values, because we
    # aggregate across different values for these tags)
    # * fall into the same aggregation bucket
    # * have the same variables (key and val), except those vals that
    # are being aggregated by.
    # so for every group of aggregation tags and variables we build a
    # list of targets that can be aggregated together

    # of course it only makes sense to agg by tags that the target
    # actually has, and that are not already constants (meaning
    # every target in the graph has the same value)

    def get_agg_key(self, agg_by_struct):
        if not agg_by_struct:
            return False

        # key with all tag_v:bucket_id for tags in agg_by_struct
        agg_id = []
        for agg_tag in sorted(set(agg_by_struct.keys()).intersection(set(self['variables'].keys()))):
            # find first bucket pattern that maches.
            # note that there should always be a catchall (''), so bucket_id should always be set
            bucket_id = next((patt for patt in agg_by_struct[agg_tag] if patt in self['variables'][agg_tag]))
            agg_id.append("%s:%s" % (agg_tag, bucket_id))
            self['match_buckets'][agg_tag] = bucket_id
        agg_id_str = ','.join(sorted(agg_id))

        # key with all variable tag_k=tag_v if tag_k not in agg_by_struct
        variables = []
        for tag_key in sorted(set(self['variables'].keys()).difference(set(agg_by_struct.keys()))):
            val = self['variables'][tag_key]
            # t can be a tuple if it's an aggregated tag
            if not isinstance(val, basestring):
                val = val[0]
            variables.append('%s=%s' % (tag_key, val))
        variables_str = ','.join(variables)
        # some values can be like "'bucket' sum (23 vals, 2 uniqs)" due to an
        # earlier aggregation. if now targets have a different amount
        # values matched, that doesn't matter and they should still
        # be aggregated together if the rest of the conditions are met
        variables_str = re.sub('\([0-9]+ vals, [0-9]+ uniqs\)', '(deets)', variables_str)

        # does this target miss one or more of the agg_by_struct keys?
        # i.e. 'sum by n1,n6' and this target only has the n1 tag.
        # put the ones that have the same missing tags together
        # and later aggregate them without that tag
        missing = []
        for tag_key in sorted(set(agg_by_struct.keys()).difference(set(self['variables'].keys()))):
            missing.append(tag_key)
        missing_str = ','.join(sorted(missing))

        agg_key = 'agg_id_found:%s__agg_id_missing:%s__variables:%s' % (agg_id_str, missing_str, variables_str)
        #from pprint import pformat
        #print "get_agg_key"
        #print "    self:", pformat(self, 8, 100)
        #print "    struct:", agg_by_struct
        #print "    resulting key:", agg_key
        return agg_key

    def get_graph_info(self, group_by):
        constants = {}
        graph_key = []
        self['variables'] = {}
        for (tag_name, tag_value) in self['tags'].items():
            if tag_name in group_by:
                if len(group_by[tag_name]) == 1:
                    assert group_by[tag_name][0] == ''
                    # only the fallback bucket, we know this will be a constant
                    constants[tag_name] = tag_value
                    graph_key.append("%s=%s" % (tag_name, tag_value))
                else:
                    bucket_id = next((patt for patt in group_by[tag_name] if patt in tag_value))
                    graph_key.append("%s:%s" % (tag_name, bucket_id))
                    self['variables'][tag_name] = tag_value
            else:
                self['variables'][tag_name] = tag_value
        graph_key = '__'.join(sorted(graph_key))
        return (graph_key, constants)


def graphite_func_aggregate(targets, agg_by_tags, aggfunc):

    aggfunc_abbrev = {
        "averageSeries": "avg",
        "sumSeries": "sum"
    }

    agg = Target({
        'target': '%s(%s)' % (aggfunc, ','.join([t['target'] for t in targets])),
        'id': [t['id'] for t in targets],
        'variables': targets[0]['variables'],
        'tags': targets[0]['tags']
    })

    # set the tags that we're aggregating by to their special values

    # differentiators is a list of tag values that set the contributing targets apart
    # this will be used later in the UI
    differentiators = {}

    # in principle every target that came in will have the same match_bucket for the given tag
    # (that's the whole point of bucketing)
    # however, some targets may end up in the aggregation without actually having the tag
    # so only set it when we find it
    bucket_id = '<none>'

    for agg_by_tag in agg_by_tags.keys():

        for t in targets:
            if agg_by_tag in t['match_buckets']:
                bucket_id = t['match_buckets'][agg_by_tag]
            differentiators[agg_by_tag] = differentiators.get(agg_by_tag, [])
            differentiators[agg_by_tag].append(t['variables'].get(agg_by_tag, '<missing>'))
        differentiators[agg_by_tag].sort()

        bucket_id_str = ''
        # note, bucket_id can be an empty string (catchall bucket),
        # in which case don't mention it explicitly
        if bucket_id:
            bucket_id_str = "'%s' " % bucket_id

        tag_val = (
            '%s%s (%d vals, %d uniqs)' % (
                bucket_id_str,
                aggfunc_abbrev.get(aggfunc, aggfunc),
                len(differentiators[agg_by_tag]),
                len(set(differentiators[agg_by_tag]))
            ),
            differentiators[agg_by_tag]
        )
        agg['variables'][agg_by_tag] = tag_val
        agg['tags'][agg_by_tag] = tag_val

    return agg
