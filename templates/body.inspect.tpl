  <div class="container-fluid">
%include templates/snippet.errors errors=errors
     <div class="row">
        <div class="span12">
          <h2>Targets</h2>
% for (target_k,target_v) in targets.items():
            Key:{{target_k}}</br>
            <table class="table">
%  for attrib_k in ('graphite_metric', 'target'):
%  attrib_v = target_v[attrib_k]
                <tr><td>{{attrib_k}}</td><td>{{attrib_v}}</td></tr>
%  end
                <tr><td>tags</td>
                <td><ul>
% for (tag_k,tag_v) in target_v["tags"].items():
    <li>{{tag_k}}:{{tag_v}}</li>
%end
                </ul></td></tr>
            </table>
%end
       </div>
      </div>
    </div> <!-- /container -->

