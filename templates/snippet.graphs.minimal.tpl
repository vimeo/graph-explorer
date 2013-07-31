<h3>{{title}}</h3>
% key = "%s_%s" % (dash, ''.join(e for e in title if e.isalnum()))
<div class="well" id="{{key}}"></div>
<script lang="javascript">
    $("#{{key}}").load("/graphs_minimal/" + encodeURIComponent("{{query}}"));
</script>
