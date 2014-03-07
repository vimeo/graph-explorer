<div class="container-fluid">
%include templates/snippet.errors errors=errors
%from urlparse import urljoin
     <div class="row">
        <h2>Rule {{rule.name()}}</h2>
        <div class="span12 well">
            <dl class="dl-horizontal span12">
                <dt>ID</dt><dd>{{rule.Id}}</dd>
                <dt>view</dt><dd>
                % if rule.is_geql():
                        <a href="{{root}}index/{{rule.expr}}"><i class="icon-fullscreen"></i></a>
                % else:
                   % url = urljoin(config.graphite_url_client, "render/?target=%s" % rule.expr)
                   <a href="{{url}}"><i class="icon-picture"></i></a>
                % end
                </dd>
                <dt>Edit</dt><dd><a href="{{root}}rules/edit/{{rule.Id}}"><i class="icon-pencil icon-white"></i></a></dd>
                <dt>Alias</dt><dd>{{rule.alias}}&nbsp;</dd>
                <dt>Expr</dt><dd>{{rule.expr}}</dd>
                <dt>Value warn</dt><dd>{{rule.val_warn}}</dd>
                <dt>Value crit</dt><dd>{{rule.val_crit}}</dd>
                <dt>Destination</dt><dd>{{rule.dest}}</dd>
                <dt>Active</dt><dd>{{'Y' if rule.active else 'N'}}</dd>
                <dt>Warn on null</dt><dd>{{'Y' if rule.warn_on_null else 'N'}}</dd>
            </dl>
            <div class="dl-horizontal span12">
                    % if rule.is_geql():
                        <div id="graph"></div>
                        <script lang="javascript">
                            $("#graph").load("{{root}}graphs_minimal_deps/" + encodeURIComponent("{{rule.expr}}"));
                        </script>
                    % else:
                        <img src="{{url}}&width=800"></img>
                    % end
           </div>
       </div>
    </div>
</div> <!-- /container -->
