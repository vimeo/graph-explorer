<div class="container-fluid">
  <div class="row-fluid">
    <div class="span3">
      <div class="well sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">Query</li>
          <li><form action="/index" method="post">
          %# http://stackoverflow.com/questions/1370021/enter-key-on-a-form-with-a-single-input-field-will-automatically-submit-with-ge
          %# http://www.carehart.org/blog/client/index.cfm/2007/5/21/enter_on_submit_fails_with_two_input_text_fields
          <input type="submit" style="display:none;"/>
          <input type="text" class="span11" data-provide="typeahead" id="query" name="query" value="{{query}}"/>
          </form></li>
          <li class="nav-header">Options</li>
          <li><a href="#" id="clearzoom">clear zoom</a></li>
        </ul>
        <script type="text/javascript">
          function update_graphs() {
            var query = $('#query')[0].value;
            $.post('/graphs/', {query:query}, function(data) {
              $('#graphs').html(data);
            });
          }
          $(document).ready(function() {
            update_graphs();
          });
        </script>
      </div><!--/.well -->
    </div><!--/span-->
    <div class="span9" id="graphs"></div>
    </div><!--/span-->
  </div><!--/row-->
</div><!--/.fluid-container-->
%# vim: ts=2 et sw=2:
