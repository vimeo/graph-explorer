<script>
    $(document).ready(function () {
        // enable the expandable labels
        // flot/tswidget doesn't have a "plot with labels is rendered" callback/hook, so we have to do a timeout. :(
        // in fact do multiple timeouts, so it works quickly, but also catches graphs that need more time to render
        [1000, 2000, 3000, 5000, 7000, 10000, 15000].forEach(function(i) {
            setTimeout(function(){
                $('.tag_label_popover').popover({"html": true, "placement": "bottom", "trigger": "hover"});
                $('.tag_label_tooltip').tooltip({"html": true, "placement": "bottom", "trigger": "hover"});
            }, i);
        });
    });
</script>
