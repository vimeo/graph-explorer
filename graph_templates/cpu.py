from graph_template import GraphTemplate
class CpuTemplate(GraphTemplate):
    pattern = "^servers\.([^\.]+)\.cpu\."

    def graph_name (self):
        self.server = self.match.groups(1)[0]
        return "cpu_%s" % self.server

    def graph_targets(self):
        targets = []
        for p in ['total.user', 'total.system', 'total.steal', 'total.softirq']:
            t = {}
            t['name'] = '%s %s' % (self.server, p)
            t['target'] = 'servers.%s.cpu.%s' % (self.server, p)
            targets.append(t)
        return targets

# vim: ts=4 et sw=4:
