import re
import convert
import copy
import unitconv
import warnings

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
        dict.__init__(self)
        tmp = copy.deepcopy(Query.default)
        self.update(tmp)
        self.parse(query_str)
        self.prepare()
        self['ast'] = self.build_ast(self['patterns'])
        self.allow_compatible_units()

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

        (query_str, self['statement']) = parse_val(query_str, '^', '(graph|list|stack|lines)\\b',
                                                   self['statement'])
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

        # doing this sanity check would now be tricky: basically you can have the same keys in more than 1 of sum/avg/group by,
        # it now depends on the bucket configuration.  since i can't wrap my head around it anymore, let's just leave it be for now.
        # it's up to people to construct sane queries, and if they do a stupid query, then at least GE shouldn't crash or anything.
        # sum_individual_keys = len(self['group_by']) + len(self['sum_by']) + len(self['avg_by'])
        # sum_unique_keys = len(set(self['group_by'].keys() + self['sum_by'].keys() + self['avg_by'].keys()))
        # if sum_individual_keys != sum_unique_keys:
        #     raise Exception("'group by' (%s), 'sum by (%s)' and 'avg by (%s)' "
        #                     "cannot list the same tag keys" %
        #                     (', '.join(self['group_by'].keys()),
        #                      ', '.join(self['sum_by'].keys()),
        #                      ', '.join(self['avg_by'].keys())))

        if avg_over_str is not None:
            # avg_over_str should be something like 'h', '10M', etc
            avg_over = re.match(avg_over_match, avg_over_str)
            if avg_over is not None:  # if None, that's an invalid request. ignore it. TODO error to user
                avg_over = avg_over.groups()
                self['avg_over'] = (int(avg_over[0]), avg_over[1])

        (query_str, self['limit_targets']) = parse_val(query_str, 'limit ', '[^ ]+', self['limit_targets'])
        self['limit_targets'] = int(self['limit_targets'])

        # split query_str into multiple patterns which are all matched independently
        # this allows you write patterns in any order, and also makes it easy to use negations
        self['patterns'] += query_str.split()

    # process the syntactic sugar
    def prepare(self):
        # we want to put these ones in front of the patterns list
        new_patterns = []
        for (tag, cfg) in self['group_by'].items():
            if tag.endswith('='):
                # add the pattern for the strong tag
                new_patterns.append(tag)
                # remove it from the struct so that from here on we have a consistent format
                # a spec coming from group by can be like 'foo=', 'foo=,bar', or 'foo=:bucket1,bar'
                self['group_by'][tag[:-1]] = cfg
                del self['group_by'][tag]
        new_patterns.extend(self['patterns'])
        self['patterns'] = new_patterns

    @staticmethod
    def apply_graphite_function_to_target(target, funcname, *args):
        def format_arg(arg):
            if isinstance(arg, basestring):
                return '"%s"' % arg
            return str(arg)
        target['target'] = "%s(%s)" % (funcname, ','.join([target['target']] + map(format_arg, args)))

    @classmethod
    def graphite_function_applier(cls, funcname, *args):
        def apply_graphite_function(target, _graph_config):
            cls.apply_graphite_function_to_target(target, funcname, *args)
        return apply_graphite_function

    @staticmethod
    def variable_applier(**tags):
        def apply_variables(target, graph_config):
            for new_k, new_v in tags.items():
                if new_k in graph_config['constants']:
                    graph_config['constants'][new_k] = new_v
                else:
                    target['variables'][new_k] = new_v
        return apply_variables

    @staticmethod
    def graph_config_applier(**configs):
        def apply_graph_config(_target, graph_config):
            graph_config.update(configs)
        return apply_graph_config

    @classmethod
    def convert_to_requested_unit_applier(cls, compatibles):
        def apply_requested_unit(target, _graph_config):
            tags = target['tags']
            try:
                scale, extra_op = compatibles[tags['unit']]
            except (KeyError, ValueError):
                # this probably means ES didn't respect the query we made,
                # or we didn't make it properly, or something? issue a warning
                # but let things go on
                warnings.warn("Found a target with unit %r which wasn't in our "
                              "list of compatible units (%r) for this query."
                              % (tags.get('unit'), compatibles.keys()),
                              RuntimeWarning)
                return
            if extra_op == 'derive':
                cls.apply_derivative_to_target(target, scale)
            else:
                if scale != 1.0:
                    cls.apply_graphite_function_to_target(target, 'scale', scale)
                if extra_op == 'integrate':
                    # graphite assumes that anything you integrate is per minute.
                    # hitcount assumes that incoming data is per second.
                    cls.apply_graphite_function_to_target(target, 'hitcount', '1min')
                    cls.apply_graphite_function_to_target(target, 'integral')
        return apply_requested_unit

    @classmethod
    def derive_counters(cls, target, _graph_config):
        if target['tags'].get('target_type') == 'counter':
            cls.apply_derivative_to_target(target, known_non_negative=True)

    @classmethod
    def apply_derivative_to_target(cls, target, scale=1, known_non_negative=False):
        wraparound = target['tags'].get('wraparound')
        if wraparound is not None:
            cls.apply_graphite_function_to_target(target, 'nonNegativeDerivative', int(wraparound))
        elif known_non_negative:
            cls.apply_graphite_function_to_target(target, 'nonNegativeDerivative')
        else:
            cls.apply_graphite_function_to_target(target, 'derivative')
        cls.apply_graphite_function_to_target(target, 'scaleToSeconds', scale)

    def allow_compatible_units(self):
        newpat, mods = self.transform_ast_for_compatible_units(self['ast'])
        if not mods:
            # no explicit unit requested; default is to apply derivative to
            # targets with target_type=counter, and leave others alone
            mods = [self.derive_counters]
        self['ast'] = newpat
        self['target_modifiers'].extend(mods)

    @classmethod
    def transform_ast_for_compatible_units(cls, ast):
        if ast[0] == 'match_tag_equality' and ast[1] == 'unit':
            requested_unit = ast[2]
            unitinfo = unitconv.parse_unitname(requested_unit, fold_scale_prefix=False)
            prefixclass = unitconv.prefix_class_for(unitinfo['scale_multiplier'])
            use_unit = unitinfo['base_unit']
            compatibles = unitconv.determine_compatible_units(**unitinfo)

            # rewrite the search term to include all the alternates
            ast = ('match_or',) + tuple(
                [('match_tag_equality', 'unit', u) for u in compatibles.keys()])

            modifiers = [
                cls.convert_to_requested_unit_applier(compatibles),
                cls.variable_applier(unit=use_unit)
            ]
            if prefixclass == 'binary':
                modifiers.append(cls.graph_config_applier(suffixes=prefixclass))
            return ast, modifiers
        elif ast[0] in ('match_and', 'match_or'):
            # recurse into subexpressions, in case they have unit=* terms
            # underneath. this won't be totally correct in case there's a way
            # to have multiple "unit=*" terms inside varying structures of
            # 'and' and 'or', but that's not exposed to the user yet anyway,
            # and auto-unit-conversion in that case probably isn't worth
            # supporting.
            new_target_modifiers = []
            newargs = []
            for sub_ast in ast[1:]:
                if isinstance(sub_ast, tuple):
                    sub_ast, mods = cls.transform_ast_for_compatible_units(sub_ast)
                    new_target_modifiers.extend(mods)
                newargs.append(sub_ast)
            ast = (ast[0],) + tuple(newargs)
            return ast, new_target_modifiers
        return ast, []

    query_pattern_re = re.compile(r'''
        # this should accept any string
        ^
        (?P<negate> ! )?
        (?P<key> [^=:]* )
        (?:
            (?P<operation> [=:] )
            (?P<term> .* )
        )?
        $
    ''', re.X)

    @classmethod
    def filtered_on(cls, query, tag):
        """
        does the given query filter on given tag? if so return first filter
        """
        # ! this assumes the ast is in the simple format without nests etc.
        for cond in query['ast']:
            if cond[0].startswith('match_tag') and cond[1] == tag:
                return cond
        return False

    @classmethod
    def build_ast(cls, patterns):
        # prepare higher performing query structure, to later match objects
        """
        if patterns looks like so:
        ['target_type=', 'unit=', '!tag_k=not_equals_thistag', 'tag_k:match_this_val', 'arbitrary', 'words']

        then the AST will look like so:
        ('match_and',
         ('!tag_k=not_equals_thistag', ('match_negate',
                                         ('match_tag_equality', 'tag_k', 'not_equals_thistag'))),
         ('target_type=',              ('match_tag_exists', 'target_type')),
         ('unit=',                     ('match_tag_exists', 'unit')),
         ('tag_k:match_this_val',      ('match_tag_regex', 'tag_k', 'match_this_val')),
         ('words',                     ('match_id_regex', 'words')),
         ('arbitrary',                 ('match_id_regex', 'arbitrary'))
        )
        """

        asts = []
        for pattern in patterns:
            matchobj = cls.query_pattern_re.match(pattern)
            oper, key, term, negate = matchobj.group('operation', 'key', 'term', 'negate')
            if oper == '=':
                if key and term:
                    ast = ('match_tag_equality', key, term)
                elif key and not term:
                    ast = ('match_tag_exists', key)
                elif term and not key:
                    ast = ('match_any_tag_value', term)
                else:
                    # pointless pattern
                    continue
            elif oper == ':':
                if key and term:
                    ast = ('match_tag_regex', key, term)
                elif key and not term:
                    ast = ('match_tag_name_regex', key)
                elif term and not key:
                    ast = ('match_tag_value_regex', key)
                else:
                    # pointless pattern
                    continue
            else:
                ast = ('match_id_regex', key)
            if negate:
                ast = ('match_negate', ast)
            asts.append(ast)
        if len(asts) == 1:
            return asts[0]
        return ('match_and',) + tuple(asts)

    # avg by foo
    # avg by foo,bar
    # avg by n3:bucketmatch1|bucketmatch2|..,othertag
    # group by target_type=,region:us-east|us-west|..
    @classmethod
    def build_buckets(cls, spec):
        # http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order
        def uniq_list(seq):
            seen = set()
            seen_add = seen.add
            return [x for x in seq if x not in seen and not seen_add(x)]
        tag_specs = spec.split(',')
        struct = {}
        for tag_spec in tag_specs:
            if ':' in tag_spec:
                tag_spec = tag_spec.split(':', 2)
                tag = tag_spec[0]
                buckets = tag_spec[1].split('|')
            else:
                tag = tag_spec
                buckets = []
            # there should always be a fallback ('' bucket), which matches all values
            # while we're add it, remove dupes
            buckets.append('')
            struct[tag] = uniq_list(buckets)
        return struct
