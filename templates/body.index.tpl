%import urllib
<div class="container-fluid">
  <div class="row-fluid">
    <div class="span3">
      <div class="well sidebar-nav">
          <div class="nav-header">Help!</div>
            <ul class="nav nav-list">
                <li><a target="_blank" href="https://github.com/vimeo/graph-explorer/wiki#getting-started">Getting started</a></li>
                <li><a target="_blank" href="https://github.com/vimeo/graph-explorer/wiki/Tutorial">Tutorial</a></li>
                <li><a target="_blank" href="https://github.com/vimeo/graph-explorer/wiki/GEQL">GEQL reference</a></li>
            </ul>
        </div>
      <div class="well sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">Query <span class="badge badge-info"><strong><a href="https://github.com/vimeo/graph-explorer/wiki/GEQL">?</a></strong></span></li>
          <li><form action="/index" method="get" onsubmit="location.href='/index/' + encodeURIComponent(this.query.value); return false;">
          %# http://stackoverflow.com/questions/1370021/enter-key-on-a-form-with-a-single-input-field-will-automatically-submit-with-ge
          %# http://www.carehart.org/blog/client/index.cfm/2007/5/21/enter_on_submit_fails_with_two_input_text_fields
          <input type="submit" style="display:none;"/>
          <input type="text" class="span11" data-provide="typeahead" id="query" name="query" value="{{query}}"/>
          </form></li>
          <!-- some day... <li class="nav-header">Options</li>
          <li><a href="#" id="clearzoom">clear zoom</a></li> -->
          <li class="nav-header">Suggested queries</li>
            {{!suggested_queries['notes']}}
            % for query in suggested_queries['queries']:
            <li>
               <a href="/index/{{urllib.quote(query['query'], "")}}">{{query['desc']}}
            </a>
            </li>
            % end
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
