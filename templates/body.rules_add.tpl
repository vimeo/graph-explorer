<div class="container-fluid">
%include templates/snippet.errors errors=errors
% setdefault('expr', '')
%from urlparse import urljoin
    <div class="row">

        <h2>Add Rule</h2>

        <form class="form-horizontal" action="/rules/add" method="post">
            <div class="control-group">
                <label class="control-label" for="expr">Expression</label>
                <div class="controls">
                    <textarea name="expr" id="expr" rows=10>{{expr}}</textarea>
                    <span class="help-block">
                        <b>Protip:</b>
                        <br/>when manually entering an expression and you want to make sure it's correct,
                        load <a href="{{config.graphite_url_client}}/render/?target=EXPRESSION">{{config.graphite_url_client}}/render/?target=EXPRESSION</a>
                        in your browser.
                        <br/> You need to see 1 graph with 1 line on it, that will be the value that will be checked.
                    </span>
                </div>
            </div>
            <div class="control-group">
                <label class="control-label" for="val_warn">Value warning</label>
                <div class="controls">
                    <input type="text" name="val_warn" id="val_warn" placeholder="value to warn at">
                </div>
            </div>
            <div class="control-group">
                <label class="control-label" for="val_crit">Value critical</label>
                <div class="controls">
                    <input type="text" name="val_crit" id="val_crit" placeholder="value to trigger critical alert at">
                </div>
            </div>
            <div class="control-group">
                <label class="control-label" for="dest">Destination (e.g. email address)</label>
                <div class="controls">
                    <input type="text" name="dest" id="dest" value="">
                </div>
            </div>
            <div class="control-group">
                <div class="controls">
                    <button type="submit" class="btn">Save</button>
                </div>
            </div>
        </form>
    </div>
</div> <!-- /container -->
