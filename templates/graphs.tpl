%include templates/snippet.errors errors=errors
% if 'query' in globals():
% if not query:
    <div class="row">
    % include templates/snippet.info msg='Empty query.  Nothing to display.'
    </div>
% end

% if query and not errors:
<script language="javascript">
tags = {{!list(tags)}};
colormap = create_colormap(tags);
count_interval = {{preferences.count_interval}};
$("#patterns").html(generate_pattern_display({{!list(query['patterns'])}}));
$("#group_by").html(generate_pattern_display({{!list(query['group_by'])}}));
</script>
    Patterns: <span id="patterns"></span><br/>
    Group by: <span id="group_by"></span><br/>
    From: {{query['from']}}<br/>
    To: {{query['to']}}<br/>
    Limit: {{query['limit_targets']}}<br/>
    Statement: {{query['statement']}}<br/>
    # targets matching: {{len_targets_matching}}/{{len_targets_all}}<br/>
    # graphs matching: {{len_graphs_matching}}/{{len_graphs_all}}<br/>
    # graphs from matching targets: {{len_graphs_targets_matching}}<br/>
    # total graphs: {{len_graphs_matching_all}}<br/>
% for (k,v) in graphs:
%     include templates/snippet.graph config=config, graph_key=k, graph_data=v, preferences=preferences
% end
% for target in targets_list:
{{target}}</br>
% end
% end
% else:
    <div class="row">
    % include templates/snippet.info msg='No query processed.  Nothing to display.'
    </div>
% end
