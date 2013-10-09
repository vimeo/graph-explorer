tags_order_pre = ['unit', 'type', 'target_type'];
tags_order_post = ['server', 'plugin'];
function display_tag(tag_name, tag_value) {
    // at some point it'll probably make sense to make the background color the inverse of the foreground color
    // cause there'll be so many foreground colors that are not always visible on any particular background.
    if (tag_value instanceof Array) {
        // v[0] -> the tag 'value' ("sumseries (x values)")
        // v [1] -> list of differentiators
        differentiators = tag_value[1];
        tag_value = tag_value[0];
        body = "<ul>";
        differentiators.forEach(function (target, i) {
            body += "<li>" + target + "</li>";
        });
        body += "</ul>";

        //$(document).ready(function() {
            // for some reason "body": "<html content>" results in an empty body, so do it via data-content attribute.
            //$('#' + label_id).popover({"html": true, "placement": "bottom", "trigger": "hover"});
        //});
        // leverage jquery to do html entity encoding, so we can put html code in the data attribute.
        title = jQuery('<div />').text('<span style="color:#' + colormap[tag_name] +';">' + tag_name + '</span>: ' + tag_value).html();
        label = "<span class='label tag_label_popover' data-original-title='" + title + "' data-content='" + body + "' ";
        label += "rel='popover' style='color:#" + colormap[tag_name] +"; background-color:#333;'>" + tag_value + "</span>";
    } else {
        title = jQuery('<div />').text('<span style="color:#' + colormap[tag_name] +';">' + tag_name + '</span>: ' + tag_value).html();
        label = "<span class='label tag_label_tooltip' data-original-title='" + title + "' ";
        label += "style='color:#" + colormap[tag_name] +"; background-color:#333;'>" + tag_value + "</span>";
    }
    return label;
}

function display_tag_for_legend(tag_name) {
    title = jQuery('<div />').text('A tag with key <span style="color:#' + colormap[tag_name] +';">' + tag_name + '</span>').html();
    label = "<span class='label tag_label_tooltip' data-original-title='" + title + "' ";
    label += "style='color:#" + colormap[tag_name] +"; background-color:#333;'>" + tag_name + "</span>";
    return label;
}

function display_word(word) {
    // word can be anything. a misc. string, a tag, a <tag>:, !<tag>=, etc
    // if it matches on a tag, display it correctly for that tag (colored label, key = parsed out tag, value the pattern)
    // otherwise generic label
    orig = word;
    if (word.charAt(0) == '!') {
        word = word.slice(1);
    }
    word = word.split('=')[0].split(':')[0];
    if (word in colormap) {
        return display_tag(word, orig);
    }
    return "<span class='label'>" + orig + "</span>";
}
// build a label list (colored or regular) for patterns which may contain tags
function generate_pattern_display(patterns) {
    var string = '';
    patterns.forEach(function(word) {string += display_word(word) });
    return string;
}
// generate label list for tags k/v, ordered by moving tags based on keys in pre post lists to begin/end.
function generate_title_from_dict(tags_dict, order_pre, order_post) {
    var title = '';
    order_pre.forEach(function(tag) {if(tag in tags_dict) {title += display_tag(tag, tags_dict[tag]); }});
    $.map(tags_dict, function (tag_v,tag) {if($.inArray(tag, order_pre) < 0 && $.inArray(tag, order_post) < 0) {title += display_tag(tag,tag_v); }});
    order_post.forEach(function(tag) {if(tag in tags_dict) {title += display_tag(tag, tags_dict[tag]); }});
    return title;
}
function generate_tag_legend_display(tags_list) {
    var title = '';
    tags_order_pre.forEach(function(tag) {if($.inArray(tag, tags_list) >= 0) {title += display_tag_for_legend(tag); }});
    tags_list.forEach(function(tag) {if($.inArray(tag, tags_order_pre) < 0 && $.inArray(tag, tags_order_post) < 0) {title += display_tag_for_legend(tag); }});
    tags_order_post.forEach(function(tag) {if($.inArray(tag, tags_list) >= 0) {title += display_tag_for_legend(tag); }});
    return title;
}
function get_graph_name(key, graph_data) {
    // set graph_name; with each tag in its own color. this way it's very clear how it's related to the query (esp. the group by)
    var graph_name = generate_title_from_dict(graph_data['constants_all'], tags_order_pre, tags_order_post);
    if(graph_name == "") {
        // this was probably a predefined graph, or at least one for which no constants are known
        graph_name = key;
    }
    return graph_name;
}
// http://stackoverflow.com/questions/280634/endswith-in-javascript
function endsWith(str, suffix) {
        return str.indexOf(suffix, str.length - suffix.length) !== -1;
}
function get_vtitle(graph_data) {
    //automatically generate vtitle, if possible
    var vtitle = "";
    var target_type = "";
    if ('type' in graph_data['constants_all']) {
        vtitle += display_tag('type', graph_data['constants_all']['type']);
    }
    if ('target_type' in graph_data['constants_all']) {
        target_type = graph_data['constants_all']['target_type'];
    }
    if ('unit' in graph_data['constants_all']) {
        if (target_type == 'counter') {
            vtitle += 'total' + display_tag('unit', graph_data['constants_all']['unit']);
        } else {
            vtitle += display_tag('unit', graph_data['constants_all']['unit']);
        }
    }
    // gauge_pct etc
    if (endsWith(target_type, '_pct')) {
        vtitle += ' %';
    }
    if (vtitle != "") {
        if (target_type == 'count') {
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
function get_inspect_url(data, name) {
    var q;
    if($.isArray(data['id'])) {
        q = data['id'].join(',');
    } else {
        q = data['id'];
    }
    return "<a href='/inspect/" + q +"'>" + name + "</a>";
}

function update_dash_entry(key) {
    var entry_input = document.getElementById('query_' + key);

    var entry_fs_link = document.getElementById('link_fullscreen_' + key);
    entry_fs_link.href = '/index/' + encodeURIComponent(entry_input.value);

    $("#viewport_" + key).load("/graphs_minimal/" + encodeURIComponent(entry_input.value));
}
function update_graphs(query, graphs) {
    var query = $(query)[0].value;
    $.post('/graphs/', {query:query}, function(data) {
        $(graphs).html(data);
    });
}

