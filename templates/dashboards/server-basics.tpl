%include templates/snippet.apply_all default_value=(apply_all_from_url or "server=fill_in_servername")
% queries = [
%   'cpu total',
%   'mem unit=B !total !vmalloc group by type:swap',
%   'stack network unit=b/s',
%   'diskspace unit=B (free|used) group by mountpoint'
% ]
% for query in queries :
    %include templates/snippet.graphs.minimal dash="server-basics", title=query, query=query
% end
