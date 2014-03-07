<div class="container-fluid">
%include templates/snippet.errors errors=errors
%from urlparse import urljoin
    <div class="arow">

        <h2>Rules</h2>

        <table class="table">
            <tr><th>rule</th><th>val_warn</th><th>val_crit</th><th>dest</th><th>active</th><th>warn on null</th></tr>
            % for rule in rules:
            <tr>
                <td>{{rule.name()}}</td>
                <td>{{rule.val_warn}}</td>
                <td>{{rule.val_crit}}</td>
                <td>{{rule.dest}}</td>
                <td>{{'Y' if rule.active else 'N'}}</td>
                <td>{{'Y' if rule.warn_on_null else 'N'}}</td>
                <td>
                    <a href="{{root}}rules/view/{{rule.Id}}"><i class="icon-eye-open icon-white"></i></a>
                    <a href="{{root}}rules/edit/{{rule.Id}}"><i class="icon-pencil icon-white"></i></a>
                    <a href="#" rule_id={{rule.Id}} rule_name="{{rule.name()}}" class="delete-link"><i class="icon-remove icon-white"></i></a>
                </td>
            </tr>
            % end
        </table>

    </div>
</div> <!-- /container -->


<script>
    $('.delete-link').on("click", function(e) {
        bootbox.confirm("Are you sure you want to delete rule '" + e.currentTarget.getAttribute("rule_name") + "'?", function(result) {
          if(result) {
              window.location.href = "{{root}}rules/delete/"+ e.currentTarget.getAttribute("rule_id");
          }
        });
    });
</script>

