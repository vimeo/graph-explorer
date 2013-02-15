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
        self.plugins = []


    def load_plugins(self):
        '''
        loads all the plugins sub-modules
        returns encountered errors, doesn't raise them because
        whoever calls this function defines how any errors are
        handled. meanwhile, loading must continue
        '''
        from plugins import Plugin
        import plugins
        errors = []
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
                errors.append(PluginError(module, "Failed to add plugin '%s'" % module, e))
                continue

            for itemname in dir(imp):
                item = getattr(imp, itemname)
                if isclass(item) and item != Plugin and issubclass(item, Plugin):
                    try:
                        self.plugins.append((module, item()))
                    # regex error is too vague to stand on its own
                    except sre_constants.error, e:
                        e = "error problem parsing matching regex: %s" % e
                        errors.append(PluginError(module, "Failed to add plugin '%s'" % module, e))
                    except Exception, e:
                        errors.append(PluginError(module, "Failed to add plugin '%s'" % module, e))
        os.chdir(wd)
        # sort plugins by their matching priority
        self.plugins = sorted(self.plugins, key=lambda t: t[1].priority, reverse=True)
        return errors

    def list_targets(self, metrics):
        targets = {}
        for metric in metrics:
            metric_matched = False
            for (i, plugin) in enumerate(self.plugins):
                (plugin_name, plugin_object) = plugin
                for (k, v) in plugin_object.find_targets(metric):
                    metric_matched = True
                    targets[k] = v
                if metric_matched:
                    break
        return targets

    def list_graphs(self, metrics):
        graphs = {}
        for plugin in self.plugins:
            (plugin_name, plugin_object) = plugin
            graphs.update(plugin_object.list_graphs(metrics))
        return graphs

