  <div class="container-fluid">
%include templates/snippet.errors errors=errors
     <div class="row">
        <div class="span12">
          <h2>Dashboards</h2>
            This is quite basic.  it just loads .py files in the 'dashboards' directory that define a list of queries.
            <br/>So basically a dashboard is a list of links from a bundle of related queries.
            <br/>Later this could become a page where the graphs for all queries are shown.
            <h3>Available dashboards</h3>
            <ul>
                % import os
                % wd = os.getcwd()
                % os.chdir('dashboards')
                % for f in os.listdir("."):
                    % if f == '__init__.py' or not f.endswith(".py"):
                        % continue
                    % end
                    % dashboard = f[:-3]
                    <li><a href="/dashboards/{{dashboard}}">{{dashboard}}</a>
                % end
                % os.chdir(wd)
            </ul>
       </div>
      </div>
    </div> <!-- /container -->

