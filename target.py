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
        variables = self['variables'].keys()
        agg_tags = set(agg_by_struct.keys()).intersection(set(variables))
        if not agg_tags:
            return None
        agg_id = []
        for agg_tag in agg_tags:
            bucket_matches = agg_by_struct[agg_tag]
            # if we can't find a better bucket_id, just use the
            # one that always represent catchall
            bucket_id = ''
            for bucket_match in bucket_matches:
                if bucket_match in self['variables'][agg_tag]:
                    bucket_id = bucket_match
                    break
            agg_id.append("%s__%s" % (agg_tag, bucket_id))
            self['match_buckets'][agg_tag] = bucket_id

        agg_id_str = '_'.join(sorted(agg_id))
        variables_str = '_'.join(
            ['%s_%s' % (k, self['variables'][k])
                for k in sorted(variables) if k not in agg_tags])
        # some values can be like "'bucket' sumSeries (8 values)" due to an
        # earlier aggregation. if now targets have a different amount
        # values matched, that doesn't matter and they should still
        # be aggregated together if the rest of the conditions are met
        variables_str = re.sub('\([0-9]+ values\)', '(Xvalues)', variables_str)
        return '%s__%s' % (agg_id_str, variables_str)
