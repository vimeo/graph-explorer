from . import Plugin


class CpuPlugin(Plugin):
    '''
    core can be individual cores as well as total.
    http://www.linuxhowtos.org/System/procstat.htm documents all states, except guest and steal(?)
    everything is in percent, but note that e.g. a 16 core machine goes up to 1600% for total.
    '''
    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.cpu\.(?P<core>[^\.]+)\.(?P<type>.*)$',
            'target_type': 'gauge_pct',
            'tags': {
                'unit': 'Jiff',
                'what': 'cpu_usage'
            }
        }
    ]

    def default_configure_target(self, target):
        if target['tags']['core'] == 'total':
            target['tags']['core'] = '_sum_'

# vim: ts=4 et sw=4:
