<div class="container-fluid">
%include templates/snippet.errors errors=errors
%from urlparse import urljoin
    <div class="arow">

        <h2>Rules</h2>

        <table class="table">
            <tr><th>expr</th><th>val_warn</th><th>val_crit</th><th>dest</th></tr>
            % for rule in rules:
            <tr>
                <td>{{rule.expr}}</td>
                <td>{{rule.val_warn}}</td>
                <td>{{rule.val_crit}}</td>
                <td>{{rule.dest}}</td>
            </tr>
            % end
        </table>

    </div>
</div> <!-- /container -->
