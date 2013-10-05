%import urllib
<div class="container-fluid">
  <div class="row-fluid">
    <div class="span3">
      <div class="well sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">Help!</li>
          <li><a target="_blank" href="https://github.com/vimeo/graph-explorer/wiki#getting-started">Getting started</a></li>
          <li><a target="_blank" href="https://github.com/vimeo/graph-explorer/wiki/Tutorial">Tutorial</a></li>
          <li><a target="_blank" href="https://github.com/vimeo/graph-explorer/wiki/GEQL">GEQL reference</a></li>
          <!-- some day... <li class="nav-header">Options</li>
          <li><a href="#" id="clearzoom">clear zoom</a></li> -->
          <li class="nav-header">Suggested queries</li>
          {{!suggested_queries['notes']}}
          % for suggested_query in suggested_queries['queries']:
            <li>
             <a href="/index/{{urllib.quote(suggested_query['query'], "")}}">{{suggested_query['desc']}}</a>
            </li>
          % end
        </ul>
      </div><!--/.well -->
    </div><!--/span-->
    <div class="span9">
      <div class="nav-header">Query <span class="badge badge-info"><strong><a href="https://github.com/vimeo/graph-explorer/wiki/GEQL">?</a></strong></span></div>
      <form action="/index" method="get" onsubmit="location.href='/index/' + encodeURIComponent(this.query.value); return false;">
        %# http://stackoverflow.com/questions/1370021/enter-key-on-a-form-with-a-single-input-field-will-automatically-submit-with-ge
        %# http://www.carehart.org/blog/client/index.cfm/2007/5/21/enter_on_submit_fails_with_two_input_text_fields
        <input type="submit" style="display:none;"/>
        <input type="text" class="span8" data-provide="typeahead" id="query" name="query" value="{{query}}"/>
      </form>
    </div>
    <div class="span9" id="graphs"></div>
  </div><!--/row-->
</div><!--/.fluid-container-->
<script type="text/javascript">
  $(document).ready(function() {
    update_graphs('#query', '#graphs');
  });
</script>
%# vim: ts=2 et sw=2:
