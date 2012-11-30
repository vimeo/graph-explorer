%import json
%#TODO print target_types on this page
  <div class="container">
     <a href="/debug/metrics">cached metrics</a>
     <div class="row">
        <div class="span12">
          <h2>Templates</h2>
          <table class="table table-condensed">
%for template in templates:
            <tr><td>{{template}}</td></tr>
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
       %data = json.dumps(graphs_targets[name],indent=1)
               <tr><td>
                       <a href="#" data-toggle="collapse" data-target="#graph-{{name}}">{{name}}</a>
                       <div id="graph-{{name}}" class="collapse"><pre>{{data}}</pre></div>
               </td></tr>
%end
	</table>
       </div>
   </div>
   <div class="row">
        <div class="span12">
          <h2>Targets</h2>
          <table class="table table-condensed">
		<tr><th>id</th><th>tags</th><th>target_type</th></tr>
%for id in sorted(targets.iterkeys()):
	% data = targets[id]
		<tr>
			<td>{{id}}</td>
			<td>
	%for tag_key in sorted(data['tags'].iterkeys()):
		% tag_val = data['tags'][tag_key]
			{{tag_key}} : {{tag_val}}<br/>
	%end
			</td>
			<td>{{data['target_type']}}</td>
		</tr>
%end
          </table>
       </div>
      </div>
    </div> <!-- /container -->

