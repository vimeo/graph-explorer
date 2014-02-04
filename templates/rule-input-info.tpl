The expression can either be a GEQL expression or a graphite target string.
If the expression contains whitespace, it's assumed to be GEQL.
<br/>If GEQL, all targets of all graphs of the GEQL result will be checked
<br/>
<b>Protip:</b>
<br/>when manually entering a graphite target string and you want to make sure it's correct,
load <a href="{{config.graphite_url_client}}/render/?target=EXPRESSION">{{config.graphite_url_client}}/render/?target=EXPRESSION</a>
in your browser.
<br/> You need to see 1 graph with 1 line on it, that will be the value that will be checked.
