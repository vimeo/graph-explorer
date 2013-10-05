%include templates/snippet.apply_all
<div class="container-fluid">
    %include templates/snippet.errors errors=errors
    <div class="row">
        <div class="span12">
            <h2>Monitoring health</h2>
            This dashboard is an experiment in using tabs.  It has known bugs:
            <ul>
                <li>tabs only display after going to the carbon tab</li>
                <li>vertical labels are a bit off</li>
                <li>"apply to all" doesn't work</li>
            </ul>
            For an elegant simple dashboard example that just works, check "graphite-machine-example"
            <div class="tabbable">
                <ul class="nav nav-tabs">
                    <li class="active"><a href="#tab1" data-toggle="tab">Statsd</a></li>
                    <li><a href="#tab2" data-toggle="tab">Carbon</a></li>
                </ul>
                <div class="tab-content">
                    <div class="tab-pane" id="tab1">
                        %include templates/snippet.graphs.minimal dash="monitoring_health_statsd", title="Statsd metrics", query="plugin=statsd"
                        %include templates/snippet.graphs.minimal dash="monitoring_health_statsd_udp", title="Statsd server udp stats", query="plugin=udp server:statsd group by type"
                    </div>
                    <div class="tab-pane" id="tab2">
                        %include templates/snippet.graphs.minimal dash="monitoring_health_carbon", title="Carbon metrics", query="plugin=carbon"
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
