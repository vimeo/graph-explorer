%try: import json
%except ImportError: import simplejson as json
%#TODO print target_types on this page
<script src="../DataTables/media/js/jquery.dataTables.js"></script>
<script src="../DataTablesPlugins/integration/bootstrap/dataTables.bootstrap.js"></script>

  <div class="container">
%include snippet.errors errors=errors
     <a href="/debug/metrics">cached metrics</a>
     <div class="row">
        <div class="span12">
          <h2>Plugins</h2>
          <table class="table table-condensed">
%for plugin in sorted(plugin_names):
            <tr><td>{{plugin}}<a href="index/plugin={{plugin}}"> <i class="icon-zoom-in icon-white"></i></a></td></tr>
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
% tags = set()
%for data in targets.itervalues():
% tags.update(data['tags'].keys())
%end
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

