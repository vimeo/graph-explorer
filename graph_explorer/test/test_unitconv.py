from __future__ import division

import doctest
import unittest
from graph_explorer import unitconv


def test_unitconv():
    # this would be lots better if we could just use py.test --doctest-modules,
    # but a bunch of other code has things that look like doctests and fail,
    # and more code which isn't protected by __name__ == "__main__" checks, and
    # py.test won't let us pick and choose modules for doctesting.
    #
    # or if we could use doctest.DocTestSuite(), that'd be nice, but that
    # would require py.test 2.3 to work, and i worry about adding dependencies
    # on things as new as that.
    doctest.testmod(unitconv)


class TestParseUnitname(unittest.TestCase):
    def test_non_fractional(self):
        self.assertDictEqual(
            unitconv.parse_unitname('Kimo'),
            {'multiplier': 1024 * 60 * 60 * 24 * 30, 'unit_class': 'time',
             'primary_unit': 's', 'base_unit': 'mo',
             'numer_multiplier': 1024 * 60 * 60 * 24 * 30, 'numer_unit_class': 'time',
             'numer_primary_unit': 's', 'numer_base_unit': 'mo'})

    def test_fractional(self):
        self.assertDictEqual(
            unitconv.parse_unitname('GB/h'),
            {'numer_multiplier': 1e9 * 8, 'denom_multiplier': 3600,
             'multiplier': 1e9 * 8 / 3600,
             'numer_unit_class': 'datasize', 'denom_unit_class': 'time',
             'unit_class': 'datasize/time',
             'numer_primary_unit': 'b', 'denom_primary_unit': 's',
             'primary_unit': 'b/s',
             'numer_base_unit': 'B', 'denom_base_unit': 'h',
             'base_unit': 'B/h'})

        self.assertDictEqual(
            unitconv.parse_unitname('kb/k', fold_scale_prefix=False),
            {'numer_multiplier': 1, 'denom_multiplier': 1,
             'multiplier': 1,
             'numer_scale_multiplier': 1000, 'denom_scale_multiplier': 1,
             'scale_multiplier': 1000,
             'numer_unit_class': 'datasize', 'denom_unit_class': None,
             'unit_class': None,
             'numer_primary_unit': 'b', 'denom_primary_unit': 'k',
             'primary_unit': 'b/k',
             'numer_base_unit': 'b', 'denom_base_unit': 'k',
             'base_unit': 'b/k'})

        self.assertDictEqual(
            unitconv.parse_unitname('Foobity/w', fold_scale_prefix=False),
            {'numer_multiplier': 1, 'denom_multiplier': 86400 * 7,
             'multiplier': 1 / (86400 * 7),
             'numer_scale_multiplier': 1, 'denom_scale_multiplier': 1,
             'scale_multiplier': 1,
             'numer_unit_class': None, 'denom_unit_class': 'time',
             'unit_class': None,
             'numer_primary_unit': 'Foobity', 'denom_primary_unit': 's',
             'primary_unit': 'Foobity/s',
             'numer_base_unit': 'Foobity', 'denom_base_unit': 'w',
             'base_unit': 'Foobity/w'})

    def test_unparseable(self):
        self.assertDictEqual(
            unitconv.parse_unitname('/w'),
            {'multiplier': 1, 'unit_class': None, 'primary_unit': '/w',
             'base_unit': '/w'})

        self.assertDictEqual(
            unitconv.parse_unitname('/'),
            {'multiplier': 1, 'unit_class': None, 'primary_unit': '/',
             'base_unit': '/'})

        self.assertDictEqual(
            unitconv.parse_unitname('a/b/c'),
            {'multiplier': 1, 'unit_class': None, 'primary_unit': 'a/b/c',
             'base_unit': 'a/b/c'})

        self.assertDictEqual(
            unitconv.parse_unitname(''),
            {'multiplier': 1, 'unit_class': None, 'primary_unit': '',
             'base_unit': ''})


def run_scenario(user_asked_for, data_exists_as, allow_derivation=True,
                 allow_integration=False, allow_prefixes_in_denominator=False,
                 round_result=6):
    userunit = unitconv.parse_unitname(user_asked_for, fold_scale_prefix=False)
    prefixclass = unitconv.prefix_class_for(userunit['scale_multiplier'])
    use_unit = userunit['base_unit']
    compatibles = unitconv.determine_compatible_units(
            allow_derivation=allow_derivation,
            allow_integration=allow_integration,
            allow_prefixes_in_denominator=allow_prefixes_in_denominator,
            **userunit)
    try:
        scale, extra_op = compatibles[data_exists_as]
    except KeyError:
        return
    if round_result is not None:
        scale = round(scale, round_result)
    return (data_exists_as, use_unit, scale, extra_op, prefixclass)


class TestDetermineCompatible(unittest.TestCase):
    def test_compatible_to_simple_primary_type(self):
        all_time_units = [pair[0] for pair in unitconv.unit_classes_by_name['time']]
        u = unitconv.determine_compatible_units('s', 'time', allow_integration=False)
        compatunits = u.keys()

        for timeunit in all_time_units:
            self.assertIn(timeunit, compatunits)

        self.assertEqual(u['MM'], (60000000.0, None))
        self.assertEqual(u['h'], (3600.0, None))

        self.assertEqual([extra_op for (_multiplier, extra_op) in u.values()],
                         [None] * len(u))

    def test_allow_derivation(self):
        u = unitconv.determine_compatible_units('b', 'datasize', 1, 's', 'time', allow_integration=False)
        self.assertEqual(u['b'], (1.0, 'derive'))
        self.assertEqual(u['B'], (8.0, 'derive'))
        self.assertEqual(u['b/s'], (1.0, None))
        self.assertAlmostEqual(u['B/d'][0], 9.26e-05)
        self.assertIsNone(u['B/d'][1])
        self.assertNotIn('h', u)

    def test_allow_integration(self):
        u = unitconv.determine_compatible_units('Eggnog', None, 0.125, allow_integration=True)
        self.assertEqual(u['Eggnog'], (8.0, None))
        self.assertAlmostEqual(u['Eggnog/h'][0], 0.0022222)
        self.assertEqual(u['Eggnog/h'][1], 'integrate')
        self.assertNotIn('derive', [extra_op for (_multiplier, extra_op) in u.values()])


class TestUnitconv(unittest.TestCase):
    # in the comments explaining results, X(t) represents a data series in
    # graphite with the "data_exists_as" unit, and Y(t) represents the data
    # series we want to graph, in the "user_asked_for" unit. the results of
    # run_scenario should give the necessary steps to convert X(t) to Y(t).

    def test_straightforward_conversion(self):
        self.assertEqual(run_scenario(user_asked_for='B', data_exists_as='b'),
                         ('b', 'B', 0.125, None, 'si'))
        # 0.125 * X(t) b = Y(t) B

    def test_esoteric_conversion_with_derive(self):
        self.assertEqual(run_scenario(user_asked_for='MiB/d', data_exists_as='kb'),
                         ('kb', 'B/d', 10800000, 'derive', 'binary'))
        # d(X(t) kb)/dt kb/s * 86400 s/d * 1B/8b * 1000 B/kB = Y(t) B/d
        # 86400 * 1000 / 8 = 10800000

    def test_unrecognized_unit_derive(self):
        self.assertEqual(run_scenario(user_asked_for='Cheese/w', data_exists_as='Cheese'),
                         ('Cheese', 'Cheese/w', 604800.0, 'derive', 'si'))
        # d(604800.0 * X(t) Cheese)/dt = Y(t) Cheese/w

    def test_integration(self):
        self.assertEqual(run_scenario(user_asked_for='b', data_exists_as='MB/s',
                                      allow_integration=True),
                         ('MB/s', 'b', 8000000.0, 'integrate', 'si'))
        # Integral(8000000.0 * X(t) MB/s, dt) = Y(t) b

    def test_conversion_between_unrecognized_units(self):
        self.assertIsNone(run_scenario(user_asked_for='pony', data_exists_as='coal'))
        # can't convert

    def test_conversion_between_units_of_different_class(self):
        self.assertIsNone(run_scenario(user_asked_for='d', data_exists_as='Mb'))
        # we know what they are but we can't convert days to megabits

    def test_straightforward_conversion_with_compound_units(self):
        self.assertEqual(run_scenario(user_asked_for='kb/s', data_exists_as='TiB/w'),
                         ('TiB/w', 'b/s', 14543804.600212, None, 'si'))
        # X(t) TiB/w * (1024**4 B/TiB) * (8 b/B) * (1 w/604800 s) = Y(t) kb/s
        # 1024**4 * 8 / 604800 =~ 14543804.600212

    def test_straightforward_conversion_between_iec_data_rates(self):
        self.assertEqual(run_scenario(user_asked_for='KiB', data_exists_as='TiB/w',
                                      allow_integration=True),
                         ('TiB/w', 'B', 1817975.575026, 'integrate', 'binary'))
        # X(t) TiB/w * (1024**4 B/TiB) * (1 w/604800 s) = Z(t) B/s
        # Integral(Z(t) KiB/s, dt) = Y(t) KiB
