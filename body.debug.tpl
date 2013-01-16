%try: import json
%except ImportError: import simplejson as json
%#TODO print target_types on this page
<script src="../DataTables/media/js/jquery.dataTables.js"></script>
<script src="../DataTablesPlugins/integration/bootstrap/dataTables.bootstrap.js"></script>

% tags = set()
%for data in targets.itervalues():
% tags.update(data['tags'].keys())
%end
% tags = sorted(tags)
% tag_values = {}
% for tag in tags:
% tag_values[tag] = set()
% end
%for data in targets.itervalues():
% for (k,v) in data['tags'].items():
%  tag_values[k].add(v)
% end
%end
% tag_values_sorted = {}
% max_values = 0
% for tag in tags:
%   tag_values_sorted[tag] = sorted(tag_values[tag])
%   max_values = max(max_values, len(tag_values[tag]))
% end

  <div class="container-fluid">
%include snippet.errors errors=errors
     <a href="/debug/metrics">cached metrics</a>
     <div class="row">
        <div class="span2">
          <h2>Plugins</h2>
          <table class="table table-condensed">
%for plugin in sorted(plugin_names):
            <tr><td>{{plugin}}<a href="index/plugin={{plugin}}"> <i class="icon-zoom-in icon-white"></i></a></td></tr>
%end
          </table>
       </div>
        <div class="span10">
          <h2>Tags seen</h2>
           <table>
                <tr>
                    %for tag in tags:
                       <th>{{tag}}</th>
                    %end
                </tr>
                %for i in range(0, max_values):
                    <tr>
                        % for tag in tags:
                            % try:
                                % v = tag_values_sorted[tag][i]
                            % except:
                                % v = ''
                            % end
                            <td>{{v}}</td>
                        % end
                    </tr>
                %end
            </table>
       </div>
     </div>
     <div class="row">
        <div class="span6">
	<h2>Graphs</h2>
          <table class="table table-condensed">
		<tr><th>name</th></tr>
%for name in sorted(graphs.iterkeys()):
       %data = json.dumps(graphs[name],indent=1)
               <tr><td>
                       <a href="#" data-toggle="collapse" data-target="#graph-{{name}}">{{name}}</a>
                       <div id="graph-{{name}}" class="collapse"><pre>{{data}}</pre></div>
               </td></tr>
%end
	</table>
       </div>
        <div class="span6">
	<h2>Graphs from targets</h2>
          <table class="table table-condensed">
		<tr><th>options</th></tr>
		<tr><td><pre>{{graphs_targets_options}}</pre></td></tr>
		<tr><th>name</th></tr>
%for name in sorted(graphs_targets.iterkeys()):
       %id = name.replace(' ','') # disallowed in var names
       %data = json.dumps(graphs_targets[name],indent=1)
               <tr><td>
                       <a href="#" data-toggle="collapse" data-target="#graph-{{id}}">{{name}}</a>
                       <div id="graph-{{id}}" class="collapse"><pre>{{data}}</pre></div>
               </td></tr>
%end
	</table>
       </div>
   </div>
   <div class="row">
        <div class="span12">
          <h2>Targets</h2>
<table cellpadding="0" cellspacing="0" border="0" class="table table-striped table-bordered" id="example">
    <thead>
        <tr>
            %for tag in tags:
                <th>{{tag}}</th>
            %end
            <th>Target</th>
        </tr>
    </thead>
    <tbody>
        % counter = 0
        %for data in targets.itervalues():
            %c = ['even','odd'][counter % 2]
            <tr class="{{c}}">
                %for tag in tags:
                    %if tag in data['tags']:
                        <td>{{data['tags'][tag]}}</td>
                    %else:
                        <td></td>
                    %end
                %end
                <td>{{data['target']}}</td>
            </tr>
            % counter += 1
        %end
    </tbody>
</table>
<script>
/* Table initialisation */
$(document).ready(function() {
    $('#example').dataTable( {
        "sDom": "<'row'<'span6'l><'span6'f>r>t<'row'<'span6'i><'span6'p>>",
        "sPaginationType": "bootstrap",
        "oLanguage": {
            "sLengthMenu": "_MENU_ records per page"
        }
    } );
} );
</script>
       </div>
      </div>
    </div> <!-- /container -->

