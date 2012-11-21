%import json
  <div class="container">
     <div class="row">
        <div class="span4">
          <h2>Metrics</h2>
          <table class="table table-condensed">
%for metric in metrics:
            <tr><td>{{metric}}</td></tr>
%end
          </table>
        </div>
        <div class="span4">
          <h2>GraphTemplates</h2>
          <table class="table table-condensed">
%for template in templates:
            <tr><td>{{template}}</td></tr>
%end
          </table>
       </div>
        <div class="span4">
          <h2>Graphs</h2>
          <table class="table table-condensed">
%for (name, data) in graphs.items():
	%data = json.dumps(data,indent=1)
		<tr><td>
			<a href="#" data-toggle="collapse" data-target="#graph-{{name}}">{{name}}</a>
			<div id="graph-{{name}}" class="collapse"><pre>{{data}}</pre></div>
		</td></tr>
%end
          </table>
       </div>
      </div>
    </div> <!-- /container -->

