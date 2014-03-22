<div class="container-fluid">
  <div class="row-fluid">
    <div class="span12">
      <div class="nav-header">Query
        <span class="badge badge-info"><a href="" target="_blank"><i class="icon-share"></i></a></span>
        <span class="badge badge-info"><a href="/rules/add" onclick="location.href='/rules/add/' + encodeURIComponent($('#query')[0].value); return false;"><i class="icon-bell"></i></a></span>
      </div>
      <form action="/index" method="get" onsubmit="location.href='/index/' + encodeURIComponent(this.query.value); return false;">
        %# http://stackoverflow.com/questions/1370021/enter-key-on-a-form-with-a-single-input-field-will-automatically-submit-with-ge
        %# http://www.carehart.org/blog/client/index.cfm/2007/5/21/enter_on_submit_fails_with_two_input_text_fields
        <input type="submit" style="display:none;"/>
        <input type="text" class="span10" data-provide="typeahead" id="query" name="query" value="{{query}}"/>
      </form>
    </div>
    <div class="span12" id="graphs"></div>
  </div><!--/row-->
</div><!--/.fluid-container-->
<script type="text/javascript">
  $(document).ready(function() {
    update_graphs('#query', '#graphs');
  });
</script>
%# vim: ts=2 et sw=2:
