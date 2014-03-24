from graph_explorer.query import Query
import copy
import unittest


def test_build_buckets_one_no_buckets():
    assert Query.build_buckets("foo") == {'foo': ['']}


def test_build_buckets_two_no_buckets():
    assert Query.build_buckets("foo,bar") == {'foo': [''], 'bar': ['']}


def test_build_buckets_two_with_buckets():
    assert Query.build_buckets("n3:bucketmatch1|bucketmatch2,othertag") == {
        'n3': ['bucketmatch1', 'bucketmatch2', ''],
        'othertag': ['']
    }


def test_build_buckets_two_with_buckets_group_by_style():
    # for 'group by', there can be '=' in there.
    assert Query.build_buckets('target_type=,region:us-east|us-west|') == {
        'target_type=': [''],
        'region': ['us-east', 'us-west', '']
    }


class _QueryTestBase(unittest.TestCase):
    maxDiff = None

    @staticmethod
    def dummyQuery(**dummydict):
        dummy = copy.deepcopy(Query.default)
        # minimal form of prepare() (syntactic sugar processing)
        # we do it this way so we know how the data structure looks like
        dummy.update({
            'patterns': ['target_type=', 'unit='],
            'group_by': {'target_type': [''], 'unit': [''], 'server': ['']}
        })
        dummy.update(dummydict)
        return dummy

    def assertQueryMatches(self, query1, query2):
        self.assertDictEqual(query1, query2)


class TestQueryBasic(_QueryTestBase):
    def test_empty(self):
        query = Query("")
        self.assertQueryMatches(query, self.dummyQuery(
            ast=(
                'match_and',
                ('match_tag_exists', 'target_type'),
                ('match_tag_exists', 'unit')
            ),
            target_modifiers=[Query.derive_counters],
            patterns=['target_type=', 'unit=']
        ))

    def test_two_simple_terms(self):
        query = Query("foo bar")
        self.assertQueryMatches(query, self.dummyQuery(
            ast=(
                'match_and',
                ('match_tag_exists', 'target_type'),
                ('match_tag_exists', 'unit'),
                ('match_id_regex', 'foo'),
                ('match_id_regex', 'bar')
            ),
            target_modifiers=[Query.derive_counters],
            patterns=['target_type=', 'unit=', 'foo', 'bar']
        ))

    def test_query_only_statement(self):
        dummy = self.dummyQuery(
            statement='list',
            ast=(
                'match_and',
                ('match_tag_exists', 'target_type'),
                ('match_tag_exists', 'unit')
            ),
            patterns=['target_type=', 'unit='],
            target_modifiers=[Query.derive_counters],
        )
        query = Query("list")
        self.assertQueryMatches(query, dummy)
        query = Query("list ")
        self.assertQueryMatches(query, dummy)


class TestQueryAdvanced(_QueryTestBase):
    def test_typo_before_sum(self):
        query = Query("octo -20hours unit=b/s memory group by foo avg by barsum by baz")
        dummy = self.dummyQuery(
            avg_by={'barsum': ['']},
            group_by={'target_type': [''], 'unit': [''], 'foo': ['']},
            patterns=['target_type=', 'unit=', 'octo', '-20hours', 'unit=b/s',
                      'memory', 'by', 'baz']
        )
        del dummy['target_modifiers']
        self.assertDictContainsSubset(dummy, query)
        ast_first_part = (
            'match_and',
            ('match_tag_exists', 'target_type'),
            ('match_tag_exists', 'unit'),
            ('match_id_regex', 'octo'),
            ('match_id_regex', '-20hours'),
        )
        ast_last_part = (
            ('match_id_regex', 'memory'),
            ('match_id_regex', 'by'),
            ('match_id_regex', 'baz')
        )
        ast = query['ast']

        self.assertTupleEqual(ast[:len(ast_first_part)],
                              ast_first_part)
        self.assertTupleEqual(ast[len(ast_first_part) + 1:],
                              ast_last_part)
        fat_hairy_or_filter = ast[len(ast_first_part)]
        self.assertEqual(fat_hairy_or_filter[0], 'match_or')
        unit_clauses = fat_hairy_or_filter[1:]
        for clause in unit_clauses:
            self.assertEqual(clause[:2], ('match_tag_equality', 'unit'))
        all_the_units = [clause[2] for clause in unit_clauses]
        for unit in ('b/s', 'MiB/s', 'PiB', 'kB/w', 'b'):
            self.assertIn(unit, all_the_units)
        self.assertTrue(any('apply_requested_unit' in str(f) for f in query['target_modifiers']),
                        msg='apply_requested_unit callback not in %r' % query['target_modifiers'])

    def test_sum_by_buckets(self):
        query = Query("stack from -20hours to -10hours avg over 10M sum by foo:bucket1|bucket2,bar min 100 max 200")
        self.assertQueryMatches(query, self.dummyQuery(**{
            'ast': (
                'match_and',
                ('match_tag_exists', 'target_type'),
                ('match_tag_exists', 'unit')
            ),
            'patterns': ['target_type=', 'unit='],
            'statement': 'stack',
            'avg_over': (10, 'M'),
            'from': '-20hours',
            'to': '-10hours',
            'min': '100',
            'max': '200',
            'sum_by': {'foo': ['bucket1', 'bucket2', ''], 'bar': ['']},
            'target_modifiers': [Query.derive_counters],
        }))

    def test_group_by_advanced(self):
        query = Query("dfvimeodfs disk srv node used group by mountpoint=:dfs1,server")
        # note: ideally, the order would be <default group by strong> + user defined group by's
        # but that was a little hard to implement
        self.assertQueryMatches(query, self.dummyQuery(**{
            'ast': (
                'match_and',
                ('match_tag_exists', 'mountpoint'),
                ('match_tag_exists', 'target_type'),
                ('match_tag_exists', 'unit'),
                ('match_id_regex', 'dfvimeodfs'),
                ('match_id_regex', 'disk'),
                ('match_id_regex', 'srv'),
                ('match_id_regex', 'node'),
                ('match_id_regex', 'used')
            ),
            'patterns': ['mountpoint=', 'target_type=', 'unit=', 'dfvimeodfs', 'disk', 'srv', 'node', 'used'],
            'group_by': {'target_type': [''], 'unit': [''], 'mountpoint': ['dfs1', ''], 'server': ['']},
            'target_modifiers': [Query.derive_counters],
        }))
