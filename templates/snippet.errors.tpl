%for (title, msg) in errors.values():
    <div class="row">
     %include templates/snippet.error title=title, msg=msg
    </div>
