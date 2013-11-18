import doctest
import unittest
import unitconv


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


def run_scenario(user_asked_for, data_exists_as, allow_derivation=True,
                 allow_integration=False, allow_prefixes_in_denominator=False,
                 round_result=6):
    userunit = unitconv.parse_unitname(user_asked_for)
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
    return (data_exists_as, scale, extra_op)


class TestUnitconv(unittest.TestCase):
    # in the comments explaining results, X(t) represents a data series in
    # graphite with the "data_exists_as" unit, and Y(t) represents the data
    # series we want to graph, in the "user_asked_for" unit. the results of
    # run_scenario should give the necessary steps to convert X(t) to Y(t).

    def test_straightforward_conversion(self):
        self.assertEqual(run_scenario(user_asked_for='B', data_exists_as='b'),
                         ('b', 0.125, None))
        # 0.125 * X(t) b = Y(t) B

    def test_esoteric_conversion_with_derive(self):
        self.assertEqual(run_scenario(user_asked_for='MiB/d', data_exists_as='kb'),
                         ('kb', 10.299683, 'derive'))
        # d(10.299683 * X(t) kb)/dt = Y(t) GiB/d

    def test_unrecognized_unit_derive(self):
        self.assertEqual(run_scenario(user_asked_for='Cheese/w', data_exists_as='Cheese'),
                         ('Cheese', 604800.0, 'derive'))
        # d(604800.0 * X(t) Cheese)/dt = Y(t) Cheese/w

    def test_integration(self):
        self.assertEqual(run_scenario(user_asked_for='b', data_exists_as='MB/s',
                                      allow_integration=True),
                         ('MB/s', 8000000.0, 'integrate'))
        # Integral(8000000.0 * X(t) MB/s, dt) = Y(t) b

    def test_conversion_between_unrecognized_units(self):
        self.assertIsNone(run_scenario(user_asked_for='pony', data_exists_as='coal'))
        # can't convert

    def test_conversion_between_units_of_different_class(self):
        self.assertIsNone(run_scenario(user_asked_for='d', data_exists_as='Mb'))
        # we know what they are but we can't convert days to megabits
