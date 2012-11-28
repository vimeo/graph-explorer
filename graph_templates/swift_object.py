from graph_template import GraphTemplate

class SwiftObjectTemplate(GraphTemplate):
    pattern       = "^stats.timers\.([^\.]+)\.object-server\.(.*)$"
    pattern_graph = "^stats.timers\.([^\.]+)\.object-server\.GET.timing.lower$"
    http_methods = ['GET', 'HEAD', 'PUT', 'REPLICATE']

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
        graphs = {}

        name = 'swift-object-server-timings-%s' % server
        targets = []
        for method in self.http_methods:
            for type in ('lower', 'upper_90'):
                t = {}
                t['name'] = '%s %s' % (server, type)
                t['target'] = 'sumSeries(stats.timers.%s.object-server.%s.%s)' % (server, method, type)
                targets.append(t)
        graphs['tpl_' + name] = {'targets': targets}

        name = 'swift-object-server-errors-%s' % server
        targets = []
        for method in self.http_methods:
            t = {}
            t['name'] = '%s %s' % (server, method)
            t['target'] = 'stats_counts.%s.object-server.%s.errors' % (server, method)
            targets.append(t)
        graphs['tpl_' + name] = {'targets': targets}

        return graphs


# vim: ts=4 et sw=4:
