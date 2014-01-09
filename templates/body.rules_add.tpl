<div class="container-fluid">
%include templates/snippet.errors errors=errors
% setdefault('metric_id', '')
%from urlparse import urljoin
    <div class="row">

        <h2>Add Rule for metric {{metric_id}}</h2>

        <form class="form-horizontal" action="/rules/add" method="post">
            <div class="control-group">
                <label class="control-label" for="metric_id">Metric_id</label>
                <div class="controls">
                    <input type="text" name="metric_id" id="metric_id" value="{{metric_id}}">
                </div>
            </div>
            <div class="control-group">
                <label class="control-label" for="expr">Expression</label>
                <div class="controls">
                    <textarea name="expr" id="expr" rows=10>{{metric_id}}</textarea>
                </div>
            </div>
            <div class="control-group">
                <label class="control-label" for="val_warn">Value warning</label>
                <div class="controls">
                    <input type="text" name="val_warn" id="val_warn" placeholder="critical to warn at">
                </div>
            </div>
            <div class="control-group">
                <label class="control-label" for="val_crit">Value critical</label>
                <div class="controls">
                    <input type="text" name="val_crit" id="val_crit" placeholder="value to error at">
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
