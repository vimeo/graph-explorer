from graph_template import GraphTemplate
class CpuTemplate(GraphTemplate):
    pattern = "^servers\.([^\.]+)\.cpu\."

    def graph_name (self, matchObject):
        self.server = matchObject.groups(1)[0]
        return "%s_cpu" % self.server

    def graph_build(self, name):
        parts = ['format=raw']
        parts_server = ['cpu.total.user', 'cpu.total.system', 'cpu.total.steal', 'cpu.total.softirq']
        url = 'render/?%s&%s' % ('&'.join(parts), '&'.join(["%s.%s" % (self.server, p) for p in parts_server]))
        return url

# vim: ts=4 et sw=4:
