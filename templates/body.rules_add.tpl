%from urlparse import urljoin
<div class="container-fluid">
    %include templates/snippet.errors errors=errors
    <div class="row">
        <h2>Add Rule</h2>
        <form class="form-horizontal span6" action="/rules/add" method="post">
            %include templates/input form=form, field='alias'
            %include templates/input form=form, field='expr', args={'rows': 10}
            %include templates/input form=form, field='val_warn', args={'placeholder': 'value to trigger warning at'}
            %include templates/input form=form, field='val_crit', args={'placeholder': 'value to trigger critical alert at'}
            %include templates/input form=form, field='dest'
            %include templates/input form=form, field='active'
            %include templates/input form=form, field='warn_on_null'
            %include templates/btn-save
        </form>
        <div class="dl-horizontal span6">
            %include templates/rule-input-info
        </div>
    </div>
</div>
