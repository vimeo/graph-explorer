%for (title, msg) in errors.values():
     %include templates/snippet.error title=title, msg=msg
%end
