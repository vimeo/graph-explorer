%include templates/snippet.apply_all
<div class="container-fluid">
    %include templates/snippet.errors errors=errors
    <div class="row">
        <div class="span12">
            <h2>Monitoring health</h2>
            <div class="tabbable">
                <ul class="nav nav-tabs">
                    <li class="active"><a href="#tab1" data-toggle="tab">Statsd</a></li>
                    <li><a href="#tab2" data-toggle="tab">Carbon</a></li>
                </ul>
                <div class="tab-content">
                    <div class="tab-pane" id="tab1">
                        %include templates/snippet.graphs.minimal dash="monitoring_health", title="Statsd metrics", query="plugin=statsd"
                        %include templates/snippet.graphs.minimal dash="monitoring_health", title="Statsd server udp stats", query="plugin=udp server:statsd group by type"
                    </div>
                    <div class="tab-pane" id="tab2">
                        %include templates/snippet.graphs.minimal dash="monitoring_health", title="Carbon metrics", query="plugin=carbon"
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
