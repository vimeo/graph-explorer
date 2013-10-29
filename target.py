import re


class Target(dict):
    def __init__(self, src_dict):
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

        # key with all tag_v:bucket_id for tags in agg_by_struct
        agg_id = []
        for agg_tag in sorted(set(agg_by_struct.keys()).intersection(set(self['variables'].keys()))):
            # find first bucket pattern that maches, or '' as fallback (catchall)
            bucket_id = next((patt for patt in agg_by_struct[agg_tag] if patt in self['variables'][agg_tag]), '')
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
        # some values can be like "'bucket' sumSeries (8 values)" due to an
        # earlier aggregation. if now targets have a different amount
        # values matched, that doesn't matter and they should still
        # be aggregated together if the rest of the conditions are met
        variables_str = re.sub('\([0-9]+ values\)', '(Xvalues)', variables_str)

        return '%s__%s' % (agg_id_str, variables_str)
