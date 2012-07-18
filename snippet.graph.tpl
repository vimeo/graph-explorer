<div class="hero-unit">
<h2>{{graph}}</h2>
<div id="chart_container_{{graph}}">
	<div id="chart_{{graph}}"></div>
	<div id="legend_container_{{graph}}">
		<div id="smoother_{{graph}}" title="Smoothing"></div>
		<div id="legend_{{graph}}"></div>
	</div>
	<div id="slider_{{graph}}"></div>
</div>
%#base_url url
<script>

// set up our data series with 50 random data points

var seriesData_{{graph}} = [ [], [], [] ];
var random_{{graph}} = new Rickshaw.Fixtures.RandomData(150);

for (var i = 0; i < 150; i++) {
	random_{{graph}}.addData(seriesData_{{graph}});
}

// instantiate our graph!

var graph_{{graph}} = new Rickshaw.Graph( {
	element: document.getElementById("chart_{{graph}}"),
	width: 960,
	height: 500,
	renderer: 'area',
	series: [
		{
			color: "#c05020",
			data: seriesData_{{graph}}[0],
			name: 'New York'
		}, {
			color: "#30c020",
			data: seriesData_{{graph}}[1],
			name: 'London'
		}, {
			color: "#6060c0",
			data: seriesData_{{graph}}[2],
			name: 'Tokyo'
		}
	]
} );

graph_{{graph}}.render();

var legend_{{graph}} = new Rickshaw.Graph.Legend( {
	graph: graph_{{graph}},
	element: document.getElementById('legend_{{graph}}')

} );

var shelving_{{graph}} = new Rickshaw.Graph.Behavior.Series.Toggle( {
	graph: graph_{{graph}},
	legend: legend_{{graph}}
} );

var highlight_{{graph}} = new Rickshaw.Graph.Behavior.Series.Highlight( {
	graph: graph_{{graph}},
	legend: legend_{{graph}}
} );

</script>

</div>
