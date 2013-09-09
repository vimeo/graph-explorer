def list_dashboards():
    import os
    wd = os.getcwd()
    os.chdir('templates/dashboards')
    dashboards = []
    for f in os.listdir("."):
        if not f.endswith(".tpl"):
            continue
        dashboards.append(f[:-4])
    os.chdir(wd)
    return sorted(dashboards)
