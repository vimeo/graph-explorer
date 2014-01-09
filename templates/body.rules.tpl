<div class="container-fluid">
%include templates/snippet.errors errors=errors
% setdefault('metric_id', '')
%from urlparse import urljoin
    <div class="arow">

        <h2>Rules {{metric_id}}</h2>

        <table class="table">
            <tr><th>metric_id</th><th>expr</th><th>val_warn</th><th>val_crit</th></tr>
            % for rule in rules:
            <tr>
                <td>{{rule.metric_id}}</td>
                <td>{{rule.expr}}</td>
                <td>{{rule.val_warn}}</td>
                <td>{{rule.val_crit}}</td>
            </tr>
            % end
        </table>

    </div>
</div> <!-- /container -->
