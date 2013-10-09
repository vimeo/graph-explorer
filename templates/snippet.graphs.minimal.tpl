% key = "%s_%s" % (dash, ''.join(e if e.isalnum() else str(ord(e)) for e in title))

<form style="display: inline;" action="javascript:void(0);">
 <input style="display: inline;" type="text" class="query_input input-xxlarge" id="query_{{key}}" data-orig-value="{{query}}" value="{{query}}">
</form>
&nbsp; &nbsp; <a href="this_needs_javascript_to_work" id="link_fullscreen_{{key}}"><i class="icon-fullscreen"></i></a>
<div class="well" id="viewport_{{key}}"></div>
<script lang="javascript">
    update_dash_entry("{{key}}");
</script>
% include templates/snippet.expand_labels
