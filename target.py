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
    # are being aggregated by (i.e. the once for which we found a bucket)
    # so for every group of buckets and values of remaining tags we build a
    # list of targets that can be aggregated together

    # of course it only makes sense to agg by tags that the target
    # actually has, and that are not already constants (meaning
    # every target in the graph has the same value)

    # TODO we might be able to merge below 2 functions

    def get_agg_key(self, agg_by_struct):
        # TODO: there's no need to treat these cases so separately.
        # buckets will use : and non-buckets = so we can just process all tags and put everything in a dict
        # and at the end just join the sorted dictkeys+val

        agg_buckets_id = {}  # stores the bucket ids for those tags that fall into a bucket
        agg_others_id = {}  # store the tag values for all other tags
        for agg_tag in set(agg_by_struct.keys()).intersection(set(self['variables'].keys())):
            # find first bucket pattern that maches.
            # there may not be a matching bucket (not even a catchall) in which case use the tag value so that
            # it won't get aggregated.
            bucket_id = next((patt for patt in agg_by_struct[agg_tag] if patt in self['variables'][agg_tag]), None)
            if bucket_id is None:
                agg_others_id[agg_tag] = self['variables'][agg_tag]
            else:
                agg_buckets_id[agg_tag] = bucket_id
            self['match_buckets'][agg_tag] = bucket_id
        agg_buckets_id_str = ','.join('%s:%s' % (tag, bucket_id) for tag in sorted(agg_buckets_id.keys()))

        for tag_key in set(self['variables'].keys()).difference(set(agg_by_struct.keys())):
            val = self['variables'][tag_key]
            # t can be a tuple if it's an aggregated tag
            if not isinstance(val, basestring):
                val = val[0]
            agg_others_id[tag_key] = val
        agg_others_id_str = ','.join('%s=%s' % (tag, val) for tag in sorted(agg_others_id.keys()))
        # some values can be like "'bucket' sumSeries (8 values)" due to an
        # earlier aggregation. if now targets have a different amount
        # values matched, that doesn't matter and they should still
        # be aggregated together if the rest of the conditions are met
        agg_others_id_str = re.sub('\([0-9]+ values\)', '(Xvalues)', agg_others_id_str)

        return '%s__%s' % (agg_buckets_id_str, agg_others_id_str)

    def get_graph_info(self, group_by):
        constants = {}
        graph_key = []
        self['variables'] = {}
        for (tag_name, tag_value) in self['tags'].items():
            if tag_name in group_by:
                if len(group_by[tag_name]) == 0:
                    # we know this will be a constant
                    constants[tag_name] = tag_value
                    graph_key.append("%s=%s" % (tag_name, tag_value))
                else:
                    bucket_id = next((patt for patt in group_by[tag_name] if patt in tag_value), None)
                    if bucket_id is None:
                        graph_key.append("%s=%s" % (tag_name, tag_value))
                    else:
                        graph_key.append("%s:%s" % (tag_name, bucket_id))
                    self['variables'][tag_name] = tag_value
            else:
                self['variables'][tag_name] = tag_value
        graph_key = '__'.join(sorted(graph_key))
        return (graph_key, constants)
