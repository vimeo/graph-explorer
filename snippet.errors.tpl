%for (title, msg) in errors.values():
    <div class="row">
     %include snippet.error title=title, msg=msg
    </div>
