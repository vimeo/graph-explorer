from query import Query
import copy
import unittest


class _QueryTestBase(unittest.TestCase):
    maxDiff = None

    def dummyQuery(self, **dummydict):
        dummy = copy.deepcopy(Query.default)
        dummy.update(dummydict)
        return dummy

    def assertQueryMatches(self, query1, query2):
        self.assertDictEqual(query1, query2)


class TestQueryBasic(_QueryTestBase):
    def test_empty(self):
        query = Query("")
        self.assertQueryMatches(query, self.dummyQuery(
            compiled_pattern=(
                'match_and',
                ('match_tag_exists', 'target_type'),
                ('match_tag_exists', 'unit')
            ),
            target_modifiers=[],
            patterns=['target_type=', 'unit=']
        ))

    def test_two_simple_terms(self):
        query = Query("foo bar")
        self.assertQueryMatches(query, self.dummyQuery(
            compiled_pattern=(
                'match_and',
                ('match_tag_exists', 'target_type'),
                ('match_tag_exists', 'unit'),
                ('match_id_regex', 'foo'),
                ('match_id_regex', 'bar')
            ),
            target_modifiers=[],
            patterns=['target_type=', 'unit=', 'foo', 'bar']
        ))

    def test_query_only_statement(self):
        dummy = self.dummyQuery(
            statement='list',
            compiled_pattern=(
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
            compiled_pattern=(
                'match_and',
                ('match_tag_exists', 'target_type'),
                ('match_tag_exists', 'unit'),
                ('match_id_regex', 'octo'),
                ('match_id_regex', '-20hours'),
                ('match_tag_equality', 'unit', 'b/s'),
                ('match_id_regex', 'memory'),
                ('match_id_regex', 'by'),
                ('match_id_regex', 'baz')
            ),
            avg_by={'barsum': ['']},
            group_by={'target_type=': [''], 'unit=': [''], 'foo': ['']},
            patterns=['target_type=', 'unit=', 'octo', '-20hours', 'unit=b/s',
                      'memory', 'by', 'baz'],
        )
        # cheat, cause we can't easily compare closures
        dummy['target_modifiers'] = query['target_modifiers'][:]
        self.assertIn('function <lambda> at', str(dummy['target_modifiers'][0]))
        self.assertIn('function apply_variables at', str(dummy['target_modifiers'][1]))
        self.assertQueryMatches(query, dummy)

    def test_regexing(self):
        query = Query("stack from -20hours to -10hours avg over 10M sum by foo:bucket1|bucket2,bar min 100 max 200")
        self.assertQueryMatches(query, self.dummyQuery(**{
            'compiled_pattern': (
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
            'sum_by': {'foo': ['bucket1', 'bucket2'], 'bar': ['']},
            'target_modifiers': [],
        }))
