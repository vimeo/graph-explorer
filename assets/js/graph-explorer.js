function display_tag(tag_name, tag_value) {
    // at some point it'll probably make sense to make the background color the inverse of the foreground color
    // cause there'll be so many foreground colors that are not always visible on any particular background.
    return "<span class='label' style='color:#" + colormap[tag_name] +"; background-color:#333;'>" + tag_value + "</span>";
}
function generate_title_from(tags, order_pre, order_post) {
    var title = '';
    order_pre.forEach(function(tag) {if(tag in tags) {title += display_tag(tag, tags[tag]); }});
    $.map(tags, function (tag_v,tag) {if($.inArray(tag, order_pre) < 0 && $.inArray(tag, order_post) < 0) {title += display_tag(tag,tag_v); }});
    order_post.forEach(function(tag) {if(tag in tags) {title += display_tag(tag, tags[tag]); }});
    return title;
}
function get_graph_name(key, graph_data) {
    // set graph_name; with each tag in its own color. this way it's very clear how it's related to the query (esp. the group by)
    var graph_name = generate_title_from(graph_data['constants_all'], ['what', 'type', 'target_type'], ['server', 'plugin']);
    if(graph_name == "") {
        // this was probably a predefined graph, or at least one for which no constants are known
        graph_name = key;
    }
    return graph_name;
}
function get_vtitle(graph_data) {
    //automatically generate vtitle, if possible
    var vtitle = "";
    var target_type = "";
    if ('target_type' in graph_data['constants_all']) {
        target_type = graph_data['constants_all']['target_type'];
    }
    if ('what' in graph_data['constants_all']) {
        if (target_type == 'counter') {
            vtitle += 'total' + display_tag('what', graph_data['constants_all']['what']);
        } else {
            vtitle += display_tag('what', graph_data['constants_all']['what']);
        }
    }
    if ('type' in graph_data['constants_all']) {
        vtitle += display_tag('type', graph_data['constants_all']['type']);
    }
    if (vtitle != "") {
        if (target_type == 'rate') {
            vtitle += "/s";
        } else if (target_type == 'count') {
            vtitle += "/" + count_interval;
        }
    }
    return vtitle;
}
function create_colormap(tags) {
    var colormap = new Array();
    tags.forEach(function(tag){colormap[tag] = (Math.round(crc32(tag)/256)).toString(16);});
    return colormap;
}
