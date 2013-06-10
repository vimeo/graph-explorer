import os
from inspect import isclass
from structured_metrics import PluginError


class Graphs(object):

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
                    except Exception, e:
                        errors.append(PluginError(module, "Failed to add plugin '%s'" % module, e))
        os.chdir(wd)
        # sort plugins by their priority
        self.plugins = sorted(self.plugins, key=lambda t: t[1].priority, reverse=True)
        return errors

    def list_graphs(self):
        graphs = {}
        for plugin in self.plugins:
            (plugin_name, plugin_object) = plugin
            graphs.update(plugin_object.get_graphs())
        return graphs
