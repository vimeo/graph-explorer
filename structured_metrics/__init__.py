import os
from inspect import isclass
import sre_constants


class PluginError(Exception):

    def __init__(self, plugin, msg, underlying_error):
        self.plugin = plugin
        self.msg = msg
        self.underlying_error = underlying_error

    def __str__(self):
        return "%s -> %s (%s)" % (self.plugin, self.msg, self.underlying_error)

class StructuredMetrics(object):

    def __init__(self):
        self.plugin_objects = []
        self.plugin_names = []


    def load_plugins(self):
        # Load all the plugins sub-modules and create a list of
        # plugin_objects and plugin_names
        from plugins import Plugin
        import plugins
        plugins_dir = os.path.dirname(plugins.__file__)
        wd = os.getcwd()
        os.chdir(plugins_dir)
        for f in os.listdir("."):
            if f == '__init__.py' or not f.endswith(".py"):
                continue
            module = f[:-3]
            try:
                imp = __import__('plugins.' + module, globals(), locals(), ['*'])
            except Exception, e:
                os.chdir(wd)
                raise PluginError(module, "Failed to add plugin '%s'" % module, e)
                continue

            for itemname in dir(imp):
                item = getattr(imp, itemname)
                if isclass(item) and item != Plugin and issubclass(item, Plugin):
                    try:
                        self.plugin_objects.append(item())
                        self.plugin_names.append(module)
                    # regex error is too vague to stand on its own
                    except sre_constants.error, e:
                        os.chdir(wd)
                        e = "error problem parsing matching regex: %s" % e
                        raise PluginError(module, "Failed to add plugin '%s'" % module, e)
                    except Exception, e:
                        os.chdir(wd)
                        raise PluginError(module, "Failed to add plugin '%s'" % module, e)
        os.chdir(wd)

    def list_targets(self, metrics):
        targets = {}
        for t_o in self.plugin_objects:
            targets.update(t_o.list_targets(metrics))
        return targets

    def list_graphs(self, metrics):
        graphs = {}
        for t_o in self.plugin_objects:
            graphs.update(t_o.list_graphs(metrics))
        return graphs

