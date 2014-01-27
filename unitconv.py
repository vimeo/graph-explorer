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


def is_power_of_2(n):
    return n & (n - 1) == 0


def prefix_class_for(multiplier):
    if multiplier > 1 \
            and (isinstance(multiplier, int) or multiplier.is_integer()) \
            and is_power_of_2(int(multiplier)):
        return 'binary'
    return 'si'


def identify_base_unit(unitname):
    for unitclassname, units in unit_classes:
        for unit_abbrev, multiplier in units:
            if unitname == unit_abbrev:
                return {'multiplier': multiplier, 'unit_class': unitclassname,
                        'primary_unit': units[0][0], 'base_unit': unitname}
    return {'multiplier': 1, 'unit_class': None, 'primary_unit': unitname,
            'base_unit': unitname}


def parse_simple_unitname(unitname, fold_scale_prefix=True):
    """
    Parse a single unit term with zero or more multiplier prefixes and one unit
    abbreviation, which may or may not be in a known unit class.

    Returns a dictionary with the following keys and values:

    'base_unit': the requested unit with any scaling prefix(es) stripped.

    'primary_unit': either the same as base_unit, or, if the unit is in one
    of the known unit classes, the primary unit for that unit class. E.g., if
    'h' (hour) were requested, the primary_unit would be 's' (second).

    'multiplier': a numeric value giving the multiplier from the primary_unit
    to the requested unit. For example, if 'kh' (kilo-hour) were requested,
    the multiplier would be 1000 * 3600 == 3600000, since a kilo-hour is
    3600000 seconds.

    'unit_class': if the requested unit was in one of the known unit classes,
    the name of that unit class. Otherwise None.

    If fold_scale_prefix is passed and false, any multiplicative factor
    imparted by a scaling prefix will be present in the key 'scale_multiplier'
    instead of being included with the 'multiplier' key.

    >>> parse_simple_unitname('Mb') == {
    ...     'multiplier': 1e6, 'unit_class': 'datasize',
    ...     'primary_unit': 'b', 'base_unit': 'b'}
    True
    >>> parse_simple_unitname('Mb', fold_scale_prefix=False) == {
    ...     'multiplier': 1, 'unit_class': 'datasize', 'primary_unit': 'b',
    ...     'scale_multiplier': 1e6, 'base_unit': 'b'}
    True
    >>> parse_simple_unitname('Err') == {
    ...     'multiplier': 1, 'unit_class': None, 'primary_unit': 'Err',
    ...     'base_unit': 'Err'}
    True
    >>> parse_simple_unitname('Kimo') == {   # "kibimonth"
    ...     'multiplier': 1024 * 86400 * 30, 'unit_class': 'time',
    ...     'primary_unit': 's', 'base_unit': 'mo'}
    True
    >>> parse_simple_unitname('MiG') == {
    ...     'multiplier': 1024 * 1024, 'unit_class': None,
    ...     'primary_unit': 'G', 'base_unit': 'G'}
    True
    >>> parse_simple_unitname('kk') == {  # "kilo-k", don't know what k unit is
    ...     'multiplier': 1000, 'unit_class': None, 'primary_unit': 'k',
    ...     'base_unit': 'k'}
    True
    >>> parse_simple_unitname('MM') == {  # "megaminute"
    ...     'multiplier': 60000000, 'unit_class': 'time',
    ...     'primary_unit': 's', 'base_unit': 'M'}
    True
    >>> parse_simple_unitname('Ki', fold_scale_prefix=False) == {
    ...     'multiplier': 1, 'unit_class': None, 'primary_unit': 'Ki',
    ...     'scale_multiplier': 1, 'base_unit': 'Ki'}
    True
    >>> parse_simple_unitname('') == {
    ...     'multiplier': 1, 'unit_class': None, 'primary_unit': '',
    ...     'base_unit': ''}
    True
    """

    # if the unitname is e.g. 'Pckt' we don't want to parse it as peta ckt's.
    # see https://github.com/vimeo/graph-explorer/wiki/Units-%26-Prefixes
    # for commonly used/standardized units
    special_units = ['Pckt', 'Msg', 'Metric', 'Ticket']

    for prefix, multiplier in multiplier_prefixes:
        if unitname.startswith(prefix) and unitname not in special_units and unitname != prefix:
            base = parse_simple_unitname(unitname[len(prefix):],
                                         fold_scale_prefix=fold_scale_prefix)
            if fold_scale_prefix:
                base['multiplier'] *= multiplier
            else:
                base['scale_multiplier'] *= multiplier
            return base
    base = identify_base_unit(unitname)
    if not fold_scale_prefix:
        base['scale_multiplier'] = 1
    return base


def parse_unitname(unitname, fold_scale_prefix=True):
    """
    Parse a unit term with at most two parts separated by / (a numerator and
    denominator, or just a plain term). Returns a structure identical to that
    returned by parse_simple_unitname(), but with extra fields for the
    numerator and for the denominator, if one exists.

    If there is a denominator, the 'base_unit', 'unit_class', 'primary_unit',
    'multiplier', and 'scale_multiplier' fields will be returned as
    combinations of the corresponding fields for the numerator and the
    denominator.

    >>> parse_unitname('GB/h') == {
    ...     'numer_multiplier': 1e9 * 9, 'denom_multiplier': 3600,
    ...     'multiplier': 1e9 * 8 / 3600,
    ...     'numer_unit_class': 'datasize', 'denom_unit_class': 'time',
    ...     'unit_class': 'datasize/time',
    ...     'numer_primary_unit': 'b', 'denom_primary_unit': 's',
    ...     'primary_unit': 'b/s',
    ...     'numer_base_unit': 'B', 'denom_base_unit': 'h',
    ...     'base_unit': 'B/h'}
    True
    """

    def copyfields(srcdict, nameprefix):
        fields = ('multiplier', 'unit_class', 'primary_unit', 'base_unit', 'scale_multiplier')
        for f in fields:
            try:
                unitstruct[nameprefix + f] = srcdict[f]
            except KeyError:
                pass

    parts = unitname.split('/', 2)
    if len(parts) > 2 or '' in parts:
        # surrender pathetically and just return the original unit
        return {'multiplier': 1, 'unit_class': None, 'primary_unit': unitname,
                'base_unit': unitname}
    unitstruct = parse_simple_unitname(parts[0], fold_scale_prefix=fold_scale_prefix)
    copyfields(unitstruct, 'numer_')
    if len(parts) == 2:
        denominator = parse_simple_unitname(parts[1], fold_scale_prefix=fold_scale_prefix)
        copyfields(denominator, 'denom_')
        unitstruct['multiplier'] /= denominator['multiplier']
        if unitstruct['unit_class'] is None or denominator['unit_class'] is None:
            unitstruct['unit_class'] = None
        else:
            unitstruct['unit_class'] += '/' + denominator['unit_class']
        unitstruct['primary_unit'] += '/' + denominator['primary_unit']
        unitstruct['base_unit'] += '/' + denominator['base_unit']
        if not fold_scale_prefix:
            unitstruct['scale_multiplier'] /= denominator['scale_multiplier']
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


def determine_compatible_units(numer_base_unit, numer_unit_class, multiplier=1,
                               denom_base_unit=None, denom_unit_class=None,
                               allow_derivation=True, allow_integration=True,
                               allow_prefixes_in_denominator=False, **_other):
    """
    Return a dict mapping unit strings to 2-tuples. The keys are all the unit
    strings that we consider compatible with the requested unit. I.e., unit
    types that we think we can convert to or from the unit the user asked for.
    The 2-tuple values in the dict are the (multiplier, extra_op) information
    explaining how to convert data of the key-unit type to unit originally
    requested by the user.

    extra_op may be None, "derive", or "integrate".
    """

    # this multiplier was for converting the other direction, so we'll use
    # the reciprocal here
    scale = 1 / multiplier

    if allow_prefixes_in_denominator:
        denom_compat_units = compat_simple_units
    else:
        denom_compat_units = compat_simple_units_noprefix

    compat_numer = compat_simple_units(numer_unit_class, numer_base_unit)
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
