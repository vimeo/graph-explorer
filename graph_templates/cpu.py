from graph_template import GraphTemplate
class CpuTemplate(GraphTemplate):
    '''
    only pass targets for total cpu metrics, not all cores individually
    '''
    pattern       = "^servers\.([^\.]+)\.cpu\.total\.(.*)$"
    pattern_graph = "^servers\.([^\.]+)\.cpu\.total\.user$"

    def generate_targets(self, match):
        server = match.groups()[0]
        type = match.groups()[1]
        t = {
            'target' : 'servers.%s.cpu.total.%s' % (server, type),
            'tags'   : {'server': server, 'type': type},
            'names'  : {'server': type, 'type': server},
            'default_group_by': 'server'
        }
        return {'targets_' + t['target']: t}

    def generate_graphs(self, match):
        '''
        http://www.linuxhowtos.org/System/procstat.htm
        guest and steal not there -> not in our graphs
        '''
        server = match.groups()[0]
        name = 'cpu-%s' % server
        # everything is in percent, but note that e.g. a 16 core machine goes up to 1600%
        targets = [
            {'name': '%s total.idle' % server,
            'target': 'servers.%s.cpu.total.idle' % server,
            'color': '#66FF66'}, # green
            {'name': '%s total.user' % server,
            'target': 'servers.%s.cpu.total.user' % server,
            'color': '#5C9DFF'}, # light blue
            {'name': '%s total.system' % server,
            'target': 'servers.%s.cpu.total.system' % server,
            'color': '#375E99'}, # dark blue
            {'name': '%s total.nice' % server,
            'target': 'servers.%s.cpu.total.nice' % server,
            'color': '#9966FF'}, # purple
            {'name': '%s total.softirq' % server,
            'target': 'servers.%s.cpu.total.softirq' % server,
            'color': '#FF3300'}, # strong red
            {'name': '%s total.irq' % server,
            'target': 'servers.%s.cpu.total.irq' % server,
            'color': '#CC2900'}, # slightly darker red (purposely very similar color)
            {'name': '%s total.iowait' % server,
            'target': 'servers.%s.cpu.total.iowait' % server,
            'color': '#FF9900'}, # orange
        ]
        return {'tpl_' + name: {'targets': targets}}

# vim: ts=4 et sw=4:
