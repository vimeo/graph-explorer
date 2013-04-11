  <div class="container-fluid">
%include templates/snippet.errors errors=errors
     <div class="row">
        <div class="span12">
          <h2>{{dashboard}}</h2>
<ul>
% for q in queries:
<li><a href="/index/{{q}}">{{q}}</a>
%end
</ul>
       </div>
      </div>
    </div> <!-- /container -->

