% # note: you must include the apply_all template:
% # the apply_all may come with a default apply_all text, and it will apply it to the queries and call update_dash_entry so that's allright
% # but if we were to call update_dash_entry() here, the default queries might be way too small and get too much data back and lock up the browser

% key = "%s_%s" % (dash, ''.join(e if e.isalnum() else str(ord(e)) for e in title))

<form style="display: inline;" action="javascript:void(0);">
 <input style="display: inline;" type="text" class="query_input input-xxlarge" id="query_{{key}}" data-orig-value="{{query}}" value="{{query}}">
</form>
&nbsp; &nbsp; <a href="this_needs_javascript_to_work" id="link_fullscreen_{{key}}"><i class="icon-fullscreen"></i></a>
<div class="well" id="viewport_{{key}}"></div>
% include templates/snippet.expand_labels
