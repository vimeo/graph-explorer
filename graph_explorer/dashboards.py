import os
import glob


def get_dirs(config):
    dirs = []
    for entry in config.locations_dashboards:
        if entry == '**builtins**':
            entry = os.path.join(os.path.dirname(__file__), 'templates/dashboards')
        dirs.append(entry)
    return dirs


def list_dashboards(config):
    dashboards = []

    for entry in get_dirs(config):
        tpl_list = glob.glob(os.path.join(entry, '*.tpl'))
        dashboards.extend(map(lambda tpl: os.path.basename(tpl)[:-4], tpl_list))
    return sorted(dashboards)
