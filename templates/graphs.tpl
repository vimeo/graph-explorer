%include templates/snippet.errors errors=errors
% if 'query' in globals():
% if not query:
    <div class="row">
    % include templates/snippet.info msg='Empty query.  Nothing to display.'
    </div>
% end

% if query and not errors:
    % def labels(l):
    %    return ' '.join(['<span class="label">%s</span>' % i for i in l])
    % end
    Patterns: {{!labels(query['patterns'])}}<br/>
    Group by: {{!labels(query['group_by'])}}<br/>
    From: {{query['from']}}<br/>
    To: {{query['to']}}<br/>
    # targets matching: {{len_targets_matching}}/{{len_targets_all}}<br/>
    # graphs matching: {{len_graphs_matching}}/{{len_graphs_all}}<br/>
    # graphs from matching targets: {{len_graphs_targets_matching}}<br/>
    # total graphs: {{len_graphs_matching_all}}<br/>
% end
% else:
    <div class="row">
    % include templates/snippet.info msg='No query processed.  Nothing to display.'
    </div>
% end
