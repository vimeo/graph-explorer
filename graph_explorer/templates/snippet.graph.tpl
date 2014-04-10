%graph_id = ''.join(e for e in graph_key if e.isalnum())
<h5 id="h5_{{graph_id}}"></h5>
%import json
%from urlparse import urljoin
        <div class="chart_container flot" id="chart_container_flot_{{graph_id}}">
            <div class="chart" id="chart_flot_{{graph_id}}" height="300px" width="700px"></div>
            <div class="legend" id="legend_flot_{{graph_id}}"></div>
            <form class="toggler" id="line_stack_form_flot_{{graph_id}}"></form>
        </div>
        <script language="javascript">
	    $(document).ready(function () {
		var graph_data = {{!json.dumps(graph_data)}};
        graph_data['constants_all'] = jQuery.extend({}, graph_data['constants'], graph_data['promoted_constants']);

        $("#h5_{{graph_id}}").html(get_graph_name("{{graph_key}}", graph_data));
        vtitle = get_vtitle(graph_data);
        if (vtitle != "") {
            graph_data["vtitle"] = vtitle;
        }

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
            // there's nothing about this target that's not already in the graph title
            if (name == "") {
                name = "empty";
            }
            return get_inspect_url(data, name);
        }
        var $msgModal = $('#scrap-modal').modal({
          backdrop: true,
          show: false,
          keyboard: false
        });

        showModal = function (data, unix_timestamp, val) {
            unix_timestamp = Math.round(unix_timestamp);
            var date = new Date(unix_timestamp * 1000);
            $msgModal
                .find('.modal-header > h3').text(data['id']).end()
                .find('.timestamp').text(unix_timestamp).end()
                .find('.datetime-local').text(date.toLocaleString()).end()
                .find('.datetime-utc').text(date.toUTCString()).end()
                 % if config.anthracite_add_url is not None:
                .find('.add_event').attr('href', '{{config.anthracite_add_url}}/ts=' + unix_timestamp).end()
                % end
                .find('.add_rule').attr('href', '/rules/add/' + data['target']).end()
                .find('.val').text(val).end()
                .modal('show');
        };

        $.map(graph_data['targets'], function (v,k) {
            v["name"] = JSON.stringify(v, null, 2);
        });
		var defaults = {
		    graphite_url: "{{urljoin(config.graphite_url_client, "render")}}",
            % if config.anthracite_host is not None:
		    events_url: "http://{{config.anthracite_host}}:{{config.anthracite_port}}/{{config.anthracite_index}}/_search",
            % end
		    from: "-24hours",
		    until: "now",
		    height: "300",
		    width: "740",
		    line_stack_toggle: 'line_stack_form_flot_{{graph_id}}',
		    series: {stack: true, lines: { show: true, lineWidth: 0, fill: true }, bars: { stack: 0 }},
		    legend: {container: '#legend_flot_{{graph_id}}', noColumns: 1, labelFormatter: labelFormatter },
            hover_details: true,
            zoneFileBasePath: '{{root}}timeserieswidget/tz',
            drawNullAsZero: true,
            tz: "{{preferences.timezone}}",
            on_click: function (label, unix_timestamp, val, event) {
                var data = JSON.parse(label);
                showModal(data, unix_timestamp, val);
            },
		};
		var graph_flot_{{graph_id}} = $.extend({}, defaults, graph_data);
        var error_cb = function(err) {
            $("#chart_flot_{{graph_id}}").append('<div class="alert alert-error"><strong>Error:<strong> ' +
                err + '</div>' + 'Check your config.py and your graphite CORS config ' +
                '(see <a href="https://github.com/vimeo/graph-explorer">README</a>).' +
                "<br/>and the network requests debugger in your browser's dev tools");
            console.log("Error: " + err);
        }
		$("#chart_flot_{{graph_id}}").graphiteFlot(graph_flot_{{graph_id}}, error_cb);
		//$("#chart_flot_{{graph_id}}").graphiteHighcharts(graph_flot_{{graph_id}}, function(err) { console.log(err); });
	});
        </script>

<!--- http://davidrs.com/wp/code-dynamic-modal-with-twitter-bootstrap-and-jquery/ -->
<div id="scrap-modal" class="modal hide fade">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
    <h3></h3>
  </div>
  <div class="modal-body">
<ul>
<li>Timestamp: <span class="timestamp"></span></li>
<li>Local Time: <span class="datetime-local"></span></li>
<li>UTC Time: <span class="datetime-utc"></span></li>
<li>Value: <span class="val"></span></li>
</ul>
    <ul>
        <li>An event happend here?  <a href="http://you-need-to-enable-anthracite-in-config-to-use-this" class="add_event">Add it to anthracite</a></li>
        <li>I want to <a href="#" class="add_rule">add an alerting rule</a> for this metric</li>
    </ul>
  </div>
  <div class="modal-footer">
    <a href="#" data-dismiss="modal" class="btn">Close</a>
    </a>
  </div>
</div>
