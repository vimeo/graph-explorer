<div class="container-fluid">
  <div class="row-fluid">
    <div class="span3">
      <div class="well sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">Pattern</li>
          <li><form action="/index" method="post">
          %# http://stackoverflow.com/questions/1370021/enter-key-on-a-form-with-a-single-input-field-will-automatically-submit-with-ge
          %# http://www.carehart.org/blog/client/index.cfm/2007/5/21/enter_on_submit_fails_with_two_input_text_fields
          <input type="submit" style="display:none;"/>
          <input type="text" data-provide="typeahead" id="pattern" name="pattern" value="{{pattern}}"/>
          </form></li>
          <li><a href="#" id="clearzoom">clear zoom</a></li>
        </ul>
        <script type="text/javascript">
          function update_graphs() {
            var pattern = $('#pattern')[0].value;
            if(pattern) {
              $.post('/graphs/', {pattern:pattern}, function(data) {
                $('#graphs').html(data);
              });
            } else {
              $('#graphs').html("Empty pattern.  Nothing to display.");
            }
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

  <hr>
    <footer>
      <p><a href="https://github.com/Dieterbe/graph-explorer">github.com</a></p>
    </footer>

</div><!--/.fluid-container-->
%# vim: ts=2 et sw=2:
