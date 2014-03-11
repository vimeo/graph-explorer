%include templates/snippet.apply_all default_value=(apply_all_from_url or "server=fill_in_servername")
% queries = [
%   'plugin=mysql',
%   'plugin=catchall_diamond n1=mysql'  # workaround until mysql plugin matches all metrics properly
% ]
% for query in queries :
    %include templates/snippet.graphs.minimal dash="mysql", title=query, query=query
% end
