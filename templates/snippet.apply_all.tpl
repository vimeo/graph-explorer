% setdefault('default_value', '')
<form action="javascript:void(0);">
  Apply to all: <input type="text" id="apply_all" name="apply_all" value="{{default_value}}"/><br>
</form>
<script>
overriding_things = [
    "avg over [^ ]+",
    "from [^ ]+",
    "group by [^ ]+",
    "GROUP BY [^ ]+",
    "avg by [^ ]+",
    "sum by [^ ]+",
    "from [^ ]+",
    "to [^ ]+",
    "limit [^ ]+"
];
$(function() {
function apply (to_apply) {
    $('.query_input').each(function(i, inp) {
        key = inp.id.replace('query_', '');
        inp = $(inp);
        val = inp.val();
        orig_q = inp.attr("data-orig-value");
        new_q = orig_q
        // usually we just want to prepend things to the query, but if you write something like 'from -2days'
        // and the query already has such a statement, we have to remove the old statement first
        $(overriding_things).each(function(i, thing) {
            patt = new RegExp(thing);
            if (new_q.match(patt) && to_apply.match(patt)) {
                console.log("both match");
                new_q = new_q.replace(patt, "");
                console.log("new_q is now " + new_q);
            }
        });
        inp.val(new_q + to_apply);
        update_dash_entry(key);
    });
}
apply(' {{default_value}}');
$("#apply_all").change(function(a) {
    apply(' ' + a.target.value);
});
});
</script>
