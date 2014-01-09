<div class="container-fluid">
%include templates/snippet.errors errors=errors
%from urlparse import urljoin
    <div class="arow">

        <h2>Rules</h2>

        <table class="table">
            <tr><th>view</th><th>expr</th><th>val_warn</th><th>val_crit</th><th>dest</th></tr>
            % for rule in rules:
            <tr>
                % if " " in rule.expr:
                    <td><a href="{{root}}index/{{rule.expr}}"><i class="icon-fullscreen"></i></a></td>
                % else:
                    <td><a href="{{urljoin(config.graphite_url_client, "render/?target=%s" % rule.expr)}}"><i class="icon-picture"></i></a></td>
                % end
                <td>{{rule.expr}}</td>
                <td>{{rule.val_warn}}</td>
                <td>{{rule.val_crit}}</td>
                <td>{{rule.dest}}</td>
            </tr>
            % end
        </table>

    </div>
</div> <!-- /container -->
