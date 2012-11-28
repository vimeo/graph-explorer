from graph_template import GraphTemplate

class SwiftObjectTemplate(GraphTemplate):
    pattern       = "^stats.timers\.([^\.]+)\.object-server\.(.*)$"
    pattern_graph = "^stats.timers\.([^\.]+)\.object-server\.GET.timing.lower$"

    def generate_targets(self, match):
        server = match.groups()[0]
        type = match.groups()[1]
        t = {
            'target' : 'stats.timers.%s.object-server.%s' % (server, type),
            'tags'   : {'server': server, 'type': type},
            'names'  : {'server': type, 'type': server},
            'default_group_by': 'server'
        }
        return {'targets_' + t['target']: t}

    def generate_graphs(self, match):
        server = match.groups()[0]
        name = 'swift-object-server-%s' % server

        targets = []
        for type in ['GET.timing.lower', 'GET.timing.upper', 'HEAD.timing.lower', 'HEAD.timing.upper',
        'PUT.timing.lower', 'PUT.timing.upper', 'REPLICATE.timing.lower', 'REPLICATE.timing.upper']:
            t = {}
            t['name'] = '%s %s' % (server, type)
            t['target'] = 'sumSeries(stats.timers.%s.object-server.%s)' % (server, type)
            targets.append(t)
        return {'tpl_' + name: {'targets': targets}}


# vim: ts=4 et sw=4:
