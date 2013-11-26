"""
Conversions between simple units and simple combinations of units, with
an eye to monitoring metrics

See https://github.com/vimeo/graph-explorer/wiki/Units-%26-Prefixes

2013 paul cannon <paul@spacemonkey.com>
"""

from __future__ import division


si_multiplier_prefixes = (
    ('k', 1000 ** 1),
    ('M', 1000 ** 2),
    ('G', 1000 ** 3),
    ('T', 1000 ** 4),
    ('P', 1000 ** 5),

    # would be easy to support these, but probably better to keep these
    # letters available for other unit names (like "Ebb"? I don't know)
    #('E', 1000 ** 6),
    #('Z', 1000 ** 7),
    #('Y', 1000 ** 8),
)

iec_multiplier_prefixes = (
    ('Ki', 1024 ** 1),
    ('Mi', 1024 ** 2),
    ('Gi', 1024 ** 3),
    ('Ti', 1024 ** 4),
    ('Pi', 1024 ** 5),

    #('Ei', 1024 ** 6),
    #('Zi', 1024 ** 7),
    #('Yi', 1024 ** 8),
)

# make sure longer prefixes are first, since some of the shorter ones
# are prefixes of the longer ones, and we iterate over them with
# .startswith() tests. So if we checked for .startswith('M') first,
# we'd never see 'Mi'. etc
multiplier_prefixes = iec_multiplier_prefixes + si_multiplier_prefixes
multiplier_prefixes_with_empty = multiplier_prefixes + (('', 1),)


second = 1
minute = second * 60
hour = minute * 60
day = hour * 24
week = day * 7
month = day * 30

times = (
    ('s', second),
    ('M', minute),
    ('h', hour),
    ('d', day),
    ('w', week),
    ('mo', month)
)

bit = 1
byte = bit * 8

datasizes = (('b', bit), ('B', byte))

unit_classes = (('time', times), ('datasize', datasizes))
unit_classes_by_name = dict(unit_classes)


def parse_simple_unitname(unitname):
    """
    Parse a single unit term with at most one multiplier prefix and one unit
    abbreviation, which may or may not be in a known unit class.

    Returns a dictionary with the following keys and values:

    'base_unit': either the requested unit with any multiplier prefix stripped,
    or, if the unit is in one of the known unit classes, the base unit for
    that unit class. E.g., if 'h' (hour) were requested, the base_unit would be
    's' (second).

    'multiplier': a numeric value giving the multiplier from the base_unit
    to the requested unit. For example, if 'kh' (kilo-hour) were requested,
    the multiplier would be 1000 * 3600 == 3600000, since a kilo-hour is
    3600000 seconds.

    'unit_class': if the requested unit was in one of the known unit classes,
    the name of that unit class. Otherwise None.

    >>> parse_simple_unitname('Mb') == {
    ...     'multiplier': 1e6, 'unit_class': 'datasize',
    ...     'base_unit': 'b'}
    True
    >>> parse_simple_unitname('Err') == {
    ...     'multiplier': 1, 'unit_class': None, 'base_unit': 'Err'}
    True
    >>> parse_simple_unitname('Kimo') == {   # "kibimonth"
    ...     'multiplier': 1024 * 86400 * 30, 'unit_class': 'time',
    ...     'base_unit': 's'}
    True
    >>> parse_simple_unitname('MiG') == {
    ...     'multiplier': 1024 * 1024, 'unit_class': None,
    ...     'base_unit': 'G'}
    True
    >>> parse_simple_unitname('kk') == {  # "kilo-k", don't know what k unit is
    ...     'multiplier': 1000, 'unit_class': None, 'base_unit': 'k'}
    True
    >>> parse_simple_unitname('MM') == {  # "megaminute"
    ...     'multiplier': 60000000, 'unit_class': 'time', 'base_unit': 's'}
    True
    >>> parse_simple_unitname('Ki') == {
    ...     'multiplier': 1, 'unit_class': None, 'base_unit': 'Ki'}
    True
    >>> parse_simple_unitname('')
    Traceback (most recent call last):
        ...
    ValueError: Empty unit passed to parse_simple_unitname
    """

    if unitname == '':
        raise ValueError('Empty unit passed to parse_simple_unitname')
    pref_mult = 1
    for prefix, multiplier in multiplier_prefixes:
        if unitname.startswith(prefix) and unitname != prefix:
            pref_mult = multiplier
            unitname = unitname[len(prefix):]
            break
    for unitclassname, units in unit_classes:
        for unit_abbrev, multiplier in units:
            if unitname == unit_abbrev:
                return {'multiplier': pref_mult * multiplier,
                        'unit_class': unitclassname,
                        'base_unit': units[0][0]}
    return {'multiplier': pref_mult,
            'unit_class': None,
            'base_unit': unitname}


def parse_unitname(unitname):
    """
    Parse a unit term with at most two parts separated by / (a numerator and
    denominator, or just a plain term). Returns a structure identical to that
    returned by parse_simple_unitname(), but with possible extra fields for
    the denominator, if one exists.

    >>> parse_unitname('Kimo') == {
    ...     'multiplier': 1024 * 2592000, 'unit_class': 'time',
    ...     'base_unit': 's'}
    True
    >>> parse_unitname('GB/h') == {
    ...     'multiplier': 1e9 * 8 / 3600, 'unit_class': 'datasize',
    ...     'base_unit': 'b', 'denom_unit_class': 'time',
    ...     'denom_base_unit': 's'}
    True
    >>> parse_unitname('kb/k') == {
    ...     'multiplier': 1000, 'unit_class': 'datasize',
    ...     'base_unit': 'b', 'denom_unit_class': None,
    ...     'denom_base_unit': 'k'}
    True
    >>> parse_unitname('Foobity/w') == {
    ...     'multiplier': 1.0 / (86400 * 7), 'unit_class': None,
    ...     'base_unit': 'Foobity', 'denom_unit_class': 'time',
    ...     'denom_base_unit': 's'}
    True
    >>> parse_unitname('/w') == {
    ...     'multiplier': 1, 'unit_class': None, 'base_unit': '/w'}
    True
    >>> parse_unitname('/') == {
    ...     'multiplier': 1, 'unit_class': None, 'base_unit': '/'}
    True
    >>> parse_unitname('a/b/c') == {
    ...     'multiplier': 1, 'unit_class': None, 'base_unit': 'a/b/c'}
    True
    >>> parse_unitname('')
    Traceback (most recent call last):
        ...
    ValueError: Empty unit passed to parse_unitname
    """

    if unitname == '':
        raise ValueError("Empty unit passed to parse_unitname")
    parts = unitname.split('/', 2)
    if len(parts) > 2 or '' in parts:
        # surrender pathetically and just return the original unit
        return {'multiplier': 1, 'unit_class': None, 'base_unit': unitname}
    unitstruct = parse_simple_unitname(parts[0])
    if len(parts) == 2:
        denominator = parse_simple_unitname(parts[1])
        unitstruct['denom_unit_class'] = denominator['unit_class']
        unitstruct['denom_base_unit'] = denominator['base_unit']
        unitstruct['multiplier'] /= denominator['multiplier']
    return unitstruct


def compat_simple_units_noprefix(unitclass, base_unit=None):
    try:
        return unit_classes_by_name[unitclass]
    except KeyError:
        return [(base_unit, 1)] if base_unit else []


def compat_simple_units(unitclass, base_unit=None):
    """
    >>> compat_simple_units('datasize', 'b')  # doctest: +NORMALIZE_WHITESPACE
    [('Kib', 1024), ('Mib', 1048576), ('Gib', 1073741824),
     ('Tib', 1099511627776), ('Pib', 1125899906842624),
     ('kb', 1000), ('Mb', 1000000), ('Gb', 1000000000),
     ('Tb', 1000000000000), ('Pb', 1000000000000000), ('b', 1),
     ('KiB', 8192), ('MiB', 8388608), ('GiB', 8589934592),
     ('TiB', 8796093022208), ('PiB', 9007199254740992),
     ('kB', 8000), ('MB', 8000000), ('GB', 8000000000),
     ('TB', 8000000000000), ('PB', 8000000000000000), ('B', 8)]
    """

    return [(prefix + base, pmult * bmult)
            for (base, bmult) in compat_simple_units_noprefix(unitclass, base_unit)
            for (prefix, pmult) in multiplier_prefixes_with_empty]


def determine_compatible_units(base_unit, unit_class, multiplier=1,
                               denom_base_unit=None, denom_unit_class=None,
                               allow_derivation=True, allow_integration=False,
                               allow_prefixes_in_denominator=False):
    """
    Return a dict mapping unit strings to 2-tuples. The keys are all the unit
    strings that we consider compatible with the requested unit. I.e., unit
    types that we think we can convert to or from the unit the user asked for.
    The 2-tuple values in the dict are the (multiplier, extra_op) information
    explaining how to convert data of the key-unit type to unit originally
    requested by the user.

    extra_op may be None, "derive", or "integrate".

    >>> all_time_units = [pair[0] for pair in unit_classes_by_name['time']]
    >>> u = determine_compatible_units('s', 'time')
    >>> set(all_time_units).issubset(u.keys())
    True
    >>> u['MM']
    (60000000.0, None)
    >>> all(extra_op is None for (multiplier, extra_op) in u.values())
    True
    >>> u['h']
    (3600.0, None)
    >>> u = determine_compatible_units('b', 'datasize', 1, 's', 'time')
    >>> u['b']
    (1.0, 'derive')
    >>> u['B']
    (8.0, 'derive')
    >>> u['b/s']
    (1.0, None)
    >>> (round(u['B/d'][0], 6), u['B/d'][1])
    (9.3e-05, None)
    >>> 'h' in u
    False
    >>> u = determine_compatible_units('Eggnog', None, 0.125, allow_integration=True)
    >>> u['Eggnog']
    (8.0, None)
    >>> (round(u['Eggnog/h'][0], 6), u['Eggnog/h'][1])
    (0.002222, 'integrate')
    >>> any(extra_op == 'derive' for (multiplier, extra_op) in u.values())
    False
    """

    # this multiplier was for converting the other direction, so we'll use
    # the reciprocal here
    scale = 1 / multiplier

    if allow_prefixes_in_denominator:
        denom_compat_units = compat_simple_units
    else:
        denom_compat_units = compat_simple_units_noprefix

    compat_numer = compat_simple_units(unit_class, base_unit)
    compat_denom = denom_compat_units(denom_unit_class, denom_base_unit)

    if denom_base_unit is None:
        # no denominator
        converteries = dict((unit, (scale * mult, None))
                            for (unit, mult) in compat_numer)
        if allow_integration:
            converteries.update(
                    (nunit + '/' + dunit, (scale * nmult / dmult, 'integrate'))
                    for (nunit, nmult) in compat_numer
                    for (dunit, dmult) in denom_compat_units('time'))
    elif allow_derivation and denom_unit_class == 'time':
        converteries = dict((unit, (scale * mult, 'derive'))
                            for (unit, mult) in compat_numer)
    else:
        converteries = {}

    converteries.update(
            (nunit + '/' + dunit, (scale * nmult / dmult, None))
            for (nunit, nmult) in compat_numer
            for (dunit, dmult) in compat_denom)

    return converteries


if __name__ == "__main__":
    import doctest
    doctest.testmod()
