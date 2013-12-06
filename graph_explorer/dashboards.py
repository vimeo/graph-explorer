import os

def list_dashboards():
    dashboards = []
    for f in os.listdir(os.path.join(os.path.dirname(__file__), "templates", "dashboards")):
        filename, extension = os.path.splitext(f)
        if extension == ".tpl":
            dashboards.append(filename)
    return sorted(dashboards)
