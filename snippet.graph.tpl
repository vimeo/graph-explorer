%graph_id = graph_key.replace('.','').replace('-','_').replace(' ','_') # disallowed in var names
<h2 id="h2_{{graph_id}}"></h2>
%try: import json
%except ImportError: import simplejson as json
        <div class="chart_container flot" id="chart_container_flot_{{graph_id}}">
            <div class="chart" id="chart_flot_{{graph_id}}" height="300px" width="700px"></div>
            <div class="legend" id="legend_flot_{{graph_id}}"></div>
            <form class="toggler" id="line_stack_form_flot_{{graph_id}}"></form>
        </div>
        <script language="javascript">
        function display_tag(tag_name, tag_value) {
            // at some point it'll probably make sense to make the background color the inverse of the foreground color
            // cause there'll be so many foreground colors that are not always visible on any particular background.
            return "<span class='label' style='color:#" + colormap[tag_name] +"; background-color:#333;'>" + tag_value + "</span>";
        }
        function generate_title_from(tags, order_pre, order_post) {
            var title = '';
            order_pre.forEach(function(tag) {if(tag in tags) {title += display_tag(tag, tags[tag]); }});
            $.map(tags, function (tag_v,tag) {if($.inArray(tag, order_pre) < 0 && $.inArray(tag, order_post) < 0) {title += display_tag(tag,tag_v); }});
            order_post.forEach(function(tag) {if(tag in tags) {title += display_tag(tag, tags[tag]); }});
            return title;
        }
	    $(document).ready(function () {
		var graph_data = {{!json.dumps(graph_data)}};

        // set graph_name; with each tag in its own color. this way it's very clear how it's related to the query (esp. the group by)
        var constants = jQuery.extend({}, graph_data['constants'], graph_data['promoted_constants']);
        graph_name = generate_title_from(constants, ['what', 'type', 'target_type'], ['server', 'plugin']);
        if(graph_name == "") {
            // this was probably a predefined graph, or at least one for which no constants are known
            graph_name = "{{graph_key}}";
        }
        $("#h2_{{graph_id}}").html(graph_name);
        //graph_data["vtitle"] = what,type and target_type as /s etc
        // interactive legend elements -> use labelFormatter (specifying name: '<a href..>foo</a>' doesn't work)
        // but this function only sees the label and series, so any extra data must be encoded in the label
        labelFormatter = function(label, series) {
            var data = JSON.parse(label);
            if(data.name) {
                // name attribute is already set. this is probably a predefined graph, not generated from targets
                return data.name;
            }
            name = "";
            // at some point, we'll probably want to order the variables; just like how we compose graph titles.
            $.map(data["variables"], function (v,k) { name += " " + display_tag(k, v);});
            // there's nothing about this target that sets it apart in the graph (i.e. only one target in the graph)
            if (name == "") {
                name = "single_target";
            }
            return "<a href='/inspect/" + data['graphite_metric'] +"'>" + name + "</a>";
        }
        $.map(graph_data['targets'], function (v,k) {
            v["name"] = JSON.stringify(v, null, 2);
        });
		var defaults = {
		    graphite_url: "{{config.graphite_url}}/render/",
            % if config.anthracite_url is not None:
		    anthracite_url: "{{config.anthracite_url}}",
            % end
		    from: "-24hours",
		    until: "now",
		    height: "300",
		    width: "740",
		    line_stack_toggle: 'line_stack_form_flot_{{graph_id}}',
		    series: {stack: true, lines: { show: true, lineWidth: 0, fill: true }},
		    xaxis: { mode: "time" },
		    legend: { container: '#legend_flot_{{graph_id}}', noColumns: 1, labelFormatter: labelFormatter },
		};
		var graph_flot_{{graph_id}} = $.extend({}, defaults, graph_data);
	        $("#chart_flot_{{graph_id}}").graphiteFlot(graph_flot_{{graph_id}}, function(err) { console.log(err); });
	});
        </script>
