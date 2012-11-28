from graph_template import GraphTemplate

class SwiftTempauthTemplate(GraphTemplate):
    pattern       = "^stats\.([^\.]+)\.tempauth\.AUTH_\.([^\.]+)$"
    pattern_graph = "^stats\.([^\.]+)\.tempauth\.AUTH_\.errors$"
    types = ['errors', 'forbidden', 'token_denied', 'unauthorized']

    def generate_targets(self, match):
        server = match.groups()[0]
        type = match.groups()[1]
        t = {
            'target' : 'stats.%s.tempauth.AUTH_.%s' % (server, type),
            'tags'   : {'server': server, 'type': type},
            'names'  : {'server': type, 'type': server},
            'default_group_by': 'server'
        }
        return {'targets_' + t['target']: t}

    def generate_graphs(self, match):
        server = match.groups()[0]
        graphs = {}

        name = 'swift-tempauth-rates-%s' % server
        targets = []
        for type in self.types:
            t = {}
            t['name'] = type
            t['target'] = 'stats.%s.tempauth.AUTH_.%s' % (server, type)
            targets.append(t)
        graphs['tpl_' + name] = {
            'targets': targets,
            'series': {'stack': False, 'lines': { 'show': True, 'lineWidth': 0.6, 'fill': False }}
        }

        name = 'swift-tempauth-counts-%s' % server
        targets = []
        for type in self.types:
            t = {}
            t['name'] = type
            t['target'] = 'stats_counts.%s.tempauth.AUTH_.%s' % (server, type)
            targets.append(t)
        graphs['tpl_' + name] = {'targets': targets}

        return graphs


# vim: ts=4 et sw=4:
