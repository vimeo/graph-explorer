from . import Plugin


class NativeProto2Plugin(Plugin):
    priority = 5
    targets = []

    def upgrade_metric(self, metric):
        """
        2 syntaxes are supported:
        * foo=bar.baz=quux
        * foo_is_bar.baz_is_quux
        because some versions of graphite-api/graphite-web struggle with =
        the 2nd format will probably prevail.
        """
        if '=' in metric or '_is_' in metric:
            if getattr(self.config, 'process_native_proto2', True):
                nodes = metric.replace('_is_', '=').split('.')
                tags = {}
                for (i, node) in enumerate(nodes):
                    if '=' in node:
                        (key, val) = node.split('=', 1)
                        # graphite fix -> Mbps -> Mb/s
                        if key == 'unit' and val.endswith('ps'):
                            val = val[:-2] + "/s"
                        tags[key] = val
                    else:
                        tags["n%d" % (i + 1)] = node
                target = {
                    'id': metric,
                    'tags': tags
                }
                return (self.get_target_id(target), target)
            else:
                return False
        return None
# vim: ts=4 et sw=4:
