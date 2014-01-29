%include templates/snippet.apply_all default_value=(apply_all_from_url or "server=fill_in_servername")
% queries = [
%   'cpu total',  # TODO make this work with collectd, who doesn't return a total. we could do sum by core, but that's less efficient for diamond
%   'mem unit=B !total !vmalloc group by type:swap',
%   'stack network unit=b/s',
%   'unit=B (free|used) group by =mountpoint'
% ]
% for query in queries :
    %include templates/snippet.graphs.minimal dash="server-basics", title=query, query=query
% end
