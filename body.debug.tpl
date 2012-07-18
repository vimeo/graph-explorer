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
%for (graph, url) in graphs.items():
%url = url.replace('&', '\n&')
		<tr><td>
			<a href="#" data-toggle="collapse" data-target="#graph-{{graph}}">{{graph}}</a>
			<div id="graph-{{graph}}" class="collapse in"><pre>{{url}}</pre></div>
		</td></tr>
%end
          </table>
		<script type="text/javascript">
                $(document).ready(function() {
                        $(".collapse").collapse()
                });
                </script>
       </div>
      </div>
    </div> <!-- /container -->

