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
        server = match.groups()[0]
        name = 'cpu-%s' % server
        targets = []
        targets.append({'name': '%s total.idle' % server,
                        'target': 'servers.%s.cpu.total.idle' % server,
                        'color': '#66FF66'})
        for type in ['total.user', 'total.system', 'total.steal', 'total.softirq']:
            t = {}
            t['name'] = '%s %s' % (server, type)
            t['target'] = 'servers.%s.cpu.%s' % (server, type)
            targets.append(t)
        return {'tpl_' + name: {'targets': targets}}

# vim: ts=4 et sw=4:
