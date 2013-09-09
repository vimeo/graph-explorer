% key = "%s_%s" % (dash, ''.join(e if e.isalnum() else str(ord(e)) for e in title))


<h3>
    {{title}}
    <a href="this_needs_javascript_to_work" id="{{key}}_link_fullscreen"><i class="icon-fullscreen"></i></a>
</h3>
<script language="javascript">
var a = document.getElementById('{{key}}_link_fullscreen');
a.href = '/index/' + encodeURIComponent("{{query}}");
</script>

<div class="well" id="{{key}}"></div>
<script lang="javascript">
    $("#{{key}}").load("/graphs_minimal/" + encodeURIComponent("{{query}}"));
</script>
