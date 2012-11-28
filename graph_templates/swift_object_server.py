from graph_template import GraphTemplate

class SwiftObjectServerTemplate(GraphTemplate):
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
        # tuples of a light with corresponding darker color
        colors = {
            'GET': ('#5C9DFF', '#375E99'), # blue
            'HEAD': ('#FFFFB2', '#FFFF00'), # yellow
            'PUT': ('#80CC80', '#009900'), # green 
            'REPLICATE': ('#694C2E', '#A59482') # brown
        }
        for method in self.http_methods:
            for type in ('lower', 'upper_90'):
                t = {}
                t['name'] = '%s %s' % (method, type)
                t['target'] = 'sumSeries(stats.timers.%s.object-server.%s.timing.%s)' % (server, method, type)
                color_key = 0 if type == 'lower' else 1
                t['color'] = colors[method][color_key]
                targets.append(t)
        graphs['tpl_' + name] = {
            'targets': targets,
            'series': {'stack': False, 'lines': { 'show': True, 'lineWidth': 0.6, 'fill': False }}
        }

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
