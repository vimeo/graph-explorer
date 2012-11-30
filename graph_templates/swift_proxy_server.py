from . import GraphTemplate

class SwiftProxyServerTemplate(GraphTemplate):
    pattern       = "^stats.timers\.([^\.]+)\.proxy-server\.(.*)$"
    pattern_graph = "^stats.timers\.([^\.]+)\.proxy-server\.account.GET.timing.lower$"
    http_methods = ['GET', 'HEAD', 'PUT', 'REPLICATE']
    target_types = {
        'swift_proxy_server': {'default_group_by': 'server'}
    }

    def generate_targets(self, match):
        server = match.groups()[0]
        type = match.groups()[1]
        t = {
            'target' : 'stats.timers.%s.proxy-server.%s' % (server, type),
            'tags'   : {'server': server, 'type': type},
            'target_type': 'swift_proxy_server'
        }
        return {'targets_' + t['target']: t}

    def generate_graphs(self, match):
        server = match.groups()[0]
        graphs = {}

        name = 'swift-proxy-server-timings-%s' % server
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
                t['target'] = 'sumSeries(stats.timers.%s.proxy-server.%s.timing.%s)' % (server, method, type)
                color_key = 0 if type == 'lower' else 1
                t['color'] = colors[method][color_key]
                targets.append(t)
        graphs['tpl_' + name] = {
            'targets': targets,
            'series': {'stack': False, 'lines': { 'show': True, 'lineWidth': 0.6, 'fill': False }}
        }

        name = 'swift-proxy-server-errors-count-%s' % server
        targets = []
        for method in self.http_methods:
            for problem in ['errors', 'timeouts']:
                targets.append({
                    'name': '%s %s' % (method, problem),
                    'target': 'stats_counts.%s.proxy-server.%s.%s' % (server, method, problem)
                })
        targets.append({
            'name': 'async_pendings',
            'target': 'stats_counts.%s.proxy-server.async_pendings' % server
        })
        graphs['tpl_' + name] = {'targets': targets}

        name = 'swift-proxy-server-errors-rate-%s' % server
        targets = []
        for method in self.http_methods:
            for problem in ['errors', 'timeouts']:
                targets.append({
                    'name': '%s %s' % (method, problem),
                    'target': 'stats.%s.proxy-server.%s.%s' % (server, method, problem)
                })
        targets.append({
            'name': 'async_pendings',
            'target': 'stats.%s.proxy-server.async_pendings' % server
        })
        graphs['tpl_' + name] = {'targets': targets}

        return graphs


# vim: ts=4 et sw=4:
