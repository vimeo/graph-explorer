<script language="javascript">
colormap = new Array();
tags = {{!list(tags)}};
tags.forEach(function(tag){colormap[tag] = (Math.round(crc32(tag)/256)).toString(16);});
count_interval = {{count_interval}};
</script>

% for (k,v) in graphs:
%     include snippet.graph config=config, graph_key=k, graph_data=v
% end
