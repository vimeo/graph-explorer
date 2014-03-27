% setdefault('page', 'index')
% import urllib
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Graph explorer</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="">
    <meta name="author" content="">

    <!-- Le styles -->
    <link href="{{root}}assets/css/bootstrap.css" rel="stylesheet">
    <style type="text/css">
      body {
        padding-top: 60px;
        padding-bottom: 40px;
      }
      .sidebar-nav {
        padding: 9px 0;
      }
    </style>

    <!-- Le HTML5 shim, for IE6-8 support of HTML5 elements -->
    <!--[if lt IE 9]>
      <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->

    <!-- Le fav and touch icons -->
    <link rel="shortcut icon" href="{{root}}assets/img/favicon.ico">
    <link rel="apple-touch-icon-precomposed" sizes="144x144" href="{{root}}assets/ico/apple-touch-icon-144-precomposed.png">
    <link rel="apple-touch-icon-precomposed" sizes="114x114" href="{{root}}assets/ico/apple-touch-icon-114-precomposed.png">
    <link rel="apple-touch-icon-precomposed" sizes="72x72" href="{{root}}assets/ico/apple-touch-icon-72-precomposed.png">
    <link rel="apple-touch-icon-precomposed" href="{{root}}assets/ico/apple-touch-icon-57-precomposed.png">
    <script src="{{root}}assets/js/jquery-1.7.2.js"></script>
    <script src="{{root}}assets/js/bootstrap.js"></script>
    <script src="{{root}}assets/js/bootbox.js"></script>
%include templates/snippet.graph-deps
  </head>

  <body>

    <div class="navbar navbar-fixed-top">
      <div class="navbar-inner">
        <div class="container-fluid">
          <a class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </a>
          <a class="brand" href="/index">Graph explorer</a>
          <div class="nav-collapse" id="main-menu">
            <ul class="nav" id="main-menu-left">
	% for (key, title) in [('index', 'Home')]:
		% if page == key:
              <li class="active"><a href="/{{key}}">{{title}}</a></li>
		% else:
              <li><a href="/{{key}}">{{title}}</a></li>
		% end
	% end
            % from graph_explorer.dashboards import list_dashboards
          <li class="dropdown" id="preview-menu">
            <a class="dropdown-toggle" data-toggle="dropdown" href="#">Dashboards <b class="caret"></b></a>
            <ul class="dropdown-menu">
                % for dashboard in list_dashboards():
                  <li><a href="/dashboard/{{dashboard}}">{{dashboard}}</a></li>
                % end
            </ul>
          </li>
          <li class="dropdown" id="preview-menu">
            <a class="dropdown-toggle" data-toggle="dropdown" href="#">Alerting <b class="caret"></b></a>
            <ul class="dropdown-menu">
                  <li><a href="/rules/">Rules</a></li>
                  <li><a href="/rules/add">Add rule</a></li>
            </ul>
          </li>
          % from graph_explorer.suggested_queries import suggested_queries
          <li class="dropdown" id="preview-menu">
            <a class="dropdown-toggle" data-toggle="dropdown" href="#">Help<b class="caret"></b></a>
            <ul class="dropdown-menu">
                  <li><a target="_blank" href="https://github.com/vimeo/graph-explorer/wiki">Documentation</a></li>
                  <li><a target="_blank" href="https://github.com/vimeo/graph-explorer/wiki#getting-started">Getting started</a></li>
                  <li><a target="_blank" href="https://github.com/vimeo/graph-explorer/wiki/the-Query-interface">UI explained</a></li>
                  <li><a target="_blank" href="https://github.com/vimeo/graph-explorer/wiki/Tutorial">Tutorial</a></li>
                  <li><a target="_blank" href="https://github.com/vimeo/graph-explorer/wiki/GEQL">GEQL (query language)</a></li>
                  <li class="divider"></li>
                  <li class="dropdown-submenu">
                      <a tabindex="-1" href="#">Query examples</a>
                      <ul class="dropdown-menu">
                      <i>{{!suggested_queries['notes']}}</i>
                      % for suggested_query in suggested_queries['queries']:
                        <li>
                         <a href="/index/{{urllib.quote(suggested_query['query'], "")}}">{{suggested_query['desc']}}</a>
                        </li>
                      % end
                      </ul>
                  </li>
            </ul>
          </li>
<li>
<p class="navbar-text">
   <span id="tag_legend"></span>
</p>
</li>

            </ul>
          </div><!--/.nav-collapse -->
            <ul class="nav pull-right">
            % if last_update is not None:
            % import time
            <li><a>last metrics update: {{time.ctime(last_update)}}</a> </li>
            % end
            </ul>
        </div>
      </div>
    </div>

{{!body}}

  </body>
</html>
