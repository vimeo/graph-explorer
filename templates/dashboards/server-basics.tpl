% # one template to show your server stats. ideally all agents report their metrics in such a way that
% # the same abstract queries can be used irrespective of plugin used
%include templates/snippet.apply_all default_value=(apply_all_from_url or "server=fill_in_servername")
% queries = [
%   'cpu sum by core',
%   'mem unit=B !total !vmalloc group by type:swap',
%   'stack network unit=b/s',
%   'unit=B (free|used) group by =mountpoint'
% ]
% for query in queries :
    %include templates/snippet.graphs.minimal dash="server-basics", title=query, query=query
% end
