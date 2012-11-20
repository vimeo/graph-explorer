<div class="hero-unit">
<h2>{{graph_name}}</h2>
%#base_url url
%import json
        <div class="chart_container flot" id="chart_container_flot_{{graph_name}}">
            <div class="chart" id="chart_flot_{{graph_name}}" height="300px" width="700px"></div>
            <div class="legend" id="legend_flot_{{graph_name}}" height="300px" width="50px" style="height:300px; width: 50px"></div>
            <form class="toggler" id="line_stack_form_flot_{{graph_name}}"></form>
        </div>
        <script language="javascript">
	    $(document).ready(function () {
		var graph_data = {{!json.dumps(graph_data)}};
		var defaults = {
		    url: "{{base_url}}/render/",
		    from: "-24hours",
		    until: "now",
		    height: "300",
		    width: "740",
		    line_stack_toggle: 'line_stack_form_flot_{{graph_name}}',
		    series: {stack: true, lines: { show: true, lineWidth: 0, fill: true }},
		    xaxis: { mode: "time" },
		    legend: { container: '#legend_flot_{{graph_name}}', noColumns: 1 },
		};
		var graph_flot_{{graph_name}} = $.extend({}, defaults, graph_data);
	        $("#chart_flot_{{graph_name}}").graphiteFlot(graph_flot_{{graph_name}}, function(err) { console.log(err); });
	});
        </script>
</div>
