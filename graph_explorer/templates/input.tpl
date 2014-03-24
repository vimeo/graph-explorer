% input = getattr(form, field)
% label = input.label(**{'class': "control-label"})
% setdefault('args', {})
<div class="control-group {{"error" if input.errors else ""}}">
    {{!label}}
    <div class="controls">
        {{!input(**args)}}
         % for error in input.errors:
             <span class="help-inline">{{error}}</span>
         % end
    </div>
</div>
