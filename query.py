import re
import convert
import copy

# note, consider "query" in the broad sense.  it is used for user input, as
# well as the blueprint config for graphs, i.e. "spec"

class Query(dict):
    default = {
        'statement': 'graph',
        'patterns': [],
        'group_by': {'target_type=': [''], 'unit=': [''], 'server': ['']},
        'sum_by': {},
        'avg_by': {},
        'avg_over': None,
        'min': None,
        'max': None,
        'from': '-24hours',
        'to': 'now',
        'limit_targets': 500,
        'target_modifiers': []
    }
    def __init__(self, query_str):
        tmp = copy.deepcopy(Query.default)
        self.update(tmp)
        self.parse(query_str)
        self.normalize()
        self.compile_patterns()

    def parse(self, query_str):
        avg_over_match = '^([0-9]*)(s|M|h|d|w|mo)$'

        # for a call like ('foo bar baz quux', 'bar ', 'baz', 'def')
        # returns ('foo quux', 'baz') or the original query and the default val if no match
        def parse_val(query_str, predicate_match, value_match, value_default=None):
            match = re.search('\\b(%s%s)' % (predicate_match, value_match), query_str)
            value = value_default
            if match and match.groups() > 0:
                value = match.groups(1)[0].replace(predicate_match, '')
                query_str = query_str[:match.start(1)] + query_str[match.end(1):]
            return (query_str, value)

        (query_str, self['statement']) = parse_val(query_str, '^', '(graph|list|stack|lines)\\b', self['statement'])
        self['statement'] = self['statement'].rstrip()

        (query_str, self['to']) = parse_val(query_str, 'to ', '[^ ]+', self['to'])
        (query_str, self['from']) = parse_val(query_str, 'from ', '[^ ]+', self['from'])

        (query_str, group_by_str) = parse_val(query_str, 'GROUP BY ', '[^ ]+')
        (query_str, extra_group_by_str) = parse_val(query_str, 'group by ', '[^ ]+')
        (query_str, sum_by_str) = parse_val(query_str, 'sum by ', '[^ ]+')
        (query_str, avg_by_str) = parse_val(query_str, 'avg by ', '[^ ]+')
        (query_str, avg_over_str) = parse_val(query_str, 'avg over ', '[^ ]+')
        (query_str, min_str) = parse_val(query_str, 'min ', '[^ ]+')
        (query_str, max_str) = parse_val(query_str, 'max ', '[^ ]+')
        explicit_group_by = {}
        if group_by_str is not None:
            explicit_group_by = Query.build_buckets(group_by_str)
            self['group_by'] = explicit_group_by
        elif extra_group_by_str is not None:
            for k in self['group_by'].keys():
                if not k.endswith('='):
                    del self['group_by'][k]
            explicit_group_by = Query.build_buckets(extra_group_by_str)
            self['group_by'].update(explicit_group_by)
        if sum_by_str is not None:
            self['sum_by'] = Query.build_buckets(sum_by_str)
        if avg_by_str is not None:
            self['avg_by'] = Query.build_buckets(avg_by_str)
        if min_str is not None:
            # check if we can parse the values, but don't actually replace yet
            # because we want to keep the 'pretty' value for now so we can display
            # it in the query details section
            convert.parse_str(min_str)
            self['min'] = min_str
        if max_str is not None:
            convert.parse_str(max_str)
            self['max'] = max_str

        # if you specified a tag in avg_by or sum_by that is included in the
        # default group_by (and you didn't explicitly ask to group by that tag), we
        # remove it from group by, so that the avg/sum can work properly.
        for tag in self['sum_by'].keys() + self['avg_by'].keys():
            for tag_check in (tag, "%s=" % tag):
                if tag_check in self['group_by'] and tag_check not in explicit_group_by.keys():
                    del self['group_by'][tag_check]

        sum_individual_keys = len(self['group_by']) + len(self['sum_by']) + len(self['avg_by'])
        sum_unique_keys = len(set(self['group_by'].keys() + self['sum_by'].keys() + self['avg_by'].keys()))
        if sum_individual_keys != sum_unique_keys:
            raise Exception("'group by' (%s), 'sum by (%s)' and 'avg by (%s)' cannot list the same tag keys" %
                            (', '.join(self['group_by'].keys()), ', '.join(self['sum_by'].keys()), ', '.join(self['avg_by'].keys())))
        if avg_over_str is not None:
            # avg_over_str should be something like 'h', '10M', etc
            avg_over = re.match(avg_over_match, avg_over_str)
            if avg_over is not None:  # if None, that's an invalid request. ignore it. TODO error to user
                avg_over = avg_over.groups()
                self['avg_over'] = (int(avg_over[0]), avg_over[1])
        for tag in self['group_by'].keys():
            if tag.endswith('='):
                self['patterns'].append(tag)

        (query_str, self['limit_targets']) = parse_val(query_str, 'limit ', '[^ ]+', self['limit_targets'])
        self['limit_targets'] = int(self['limit_targets'])

        # split query_str into multiple patterns which are all matched independently
        # this allows you write patterns in any order, and also makes it easy to use negations
        self['patterns'] += query_str.split()


    def normalize(self):
        unit_conversions = {
            '/M': ['scale', '60'],
            '/h': ['scale', '3600'],
            '/d': ['scale', str(3600 * 24)],
            '/w': ['scale', str(3600 * 24 * 7)],
            '/mo': ['scale', str(3600 * 24 * 30)]
        }
        for (i, pattern) in enumerate(self['patterns']):
            if pattern.startswith('unit='):
                unit = pattern.split('=')[1]
                for (divisor, modifier) in unit_conversions.items():
                    if unit.endswith(divisor):
                        real_unit = unit
                        unit = "%s/s" % unit[0:-(len(divisor))]
                        self['patterns'][i] = "unit=%s" % unit
                        self['target_modifiers'].append({'target': modifier, 'tags': {'unit': real_unit}})
                        break


    def compile_patterns(self):
        # prepare higher performing query structure, to later match objects
        # note that if you have twice the exact same "word" (ignoring leading '!'), the last one wins
        """
        if self['patterns'] looks like so:
        ['target_type=', 'what=', '!tag_k=not_equals_thistag_v', 'tag_k:match_this_val', 'arbitrary', 'words']

        then the patterns will look like so:
        {
        'tag_k=not_equals_thistag_v': {'negate': True, 'match_tag_equality': ['tag_k', 'not_equals_thistag_v']},
        'target_type=':               {'negate': False, 'match_tag_equality': ['target_type', '']},
        'what=':                      {'negate': False, 'match_tag_equality': ['what', '']},
        'tag_k:match_this_val':       {'negate': False, 'match_tag_regex': ['tag_k', 'match_this_val']},
        'words':                      {'negate': False, 'match_id_regex': <_sre.SRE_Pattern object at 0x2612cb0>},
        'arbitrary':                  {'negate': False, 'match_id_regex': <_sre.SRE_Pattern object at 0x7f6cc000bd90>}
        }
        """
        patterns = {}
        for pattern in self['patterns']:
            negate = False
            if pattern.startswith('!'):
                negate = True
                pattern = pattern[1:]
            patterns[pattern] = {'negate': negate}
            if '=' in pattern:
                patterns[pattern]['match_tag_equality'] = pattern.split('=')
            elif ':' in pattern:
                patterns[pattern]['match_tag_regex'] = pattern.split(':')
            else:
                patterns[pattern]['match_id_regex'] = re.compile(pattern)
        self['compiled_patterns'] = patterns


    # avg by foo
    # avg by foo,bar
    # avg by n3:bucketmatch1|bucketmatch2|..,othertag
    # group by target_type=,region:us-east|us-west|..
    @classmethod
    def build_buckets(cls, spec):
        tag_specs = spec.split(',')
        struct = {}
        for tag_spec in tag_specs:
            if ':' in tag_spec:
                tag_spec = tag_spec.split(':', 2)
                buckets = tag_spec[1].split('|')
                struct[tag_spec[0]] = buckets
            else:
                # this tag has one bucket, the empty string, which matches all
                # values
                struct[tag_spec] = ['']
        return struct
