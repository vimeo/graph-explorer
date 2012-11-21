from graph_template import GraphTemplate
class SwiftObjectTemplate(GraphTemplate):
    pattern = "^stats.timers\.([^\.]+)\.object-server\."

    def graph_name (self):
        self.server = self.match.groups(1)[0]
        return "swift_object_%s" % self.server

    def graph_targets(self):
        targets = []
        for p in ['GET.timing.lower', 'GET.timing.upper', 'HEAD.timing.lower', 'HEAD.timing.upper',
  'PUT.timing.lower', 'PUT.timing.upper', 'REPLICATE.timing.lower', 'REPLICATE.timing.upper']:
            t = {}
            t['name'] = '%s %s' % (self.server, p)
            t['target'] = 'sumSeries(stats.timers.%s.object-server.%s)' % (self.server, p)
            targets.append(t)
        return targets

# vim: ts=4 et sw=4:
