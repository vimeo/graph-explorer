import os
import glob


def list_dashboards():
    tpl_list = glob.glob(os.path.join(os.path.dirname(__file__),'templates/dashboards/*.tpl'))
    dashboards = map(lambda tpl: os.path.basename(tpl)[:-4], tpl_list)
    return sorted(dashboards)
