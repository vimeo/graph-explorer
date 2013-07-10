  <div class="container-fluid">
%include templates/snippet.errors errors=errors
     <div class="row">
        <div class="span12">
          <h2>Targets</h2>
% print metrics
% for metric in metrics:
            Key:{{metric['id']}}</br>
            <table class="table">
                <tr><td>tags</td>
                <td><ul>
                % for (tag_k,tag_v) in metric['tags'].items():
                    <li>{{tag_k}}:{{tag_v}}</li>
                %end
                </ul></td></tr>
            </table>
%end
       </div>
      </div>
    </div> <!-- /container -->
