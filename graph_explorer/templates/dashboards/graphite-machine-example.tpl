%include templates/snippet.apply_all
% queries = [
%   'server:graphite diskspace unit=B used',
%   'server:graphite inodes free'
% ]

% for query in queries :
    %include templates/snippet.graphs.minimal dash="graphite_machine_example", title=query, query=query
% end
