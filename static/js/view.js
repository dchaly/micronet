
// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function is_valid_ipv4_addr(ip) {
  return /^(?=\d+\.\d+\.\d+\.\d+$)(?:(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]|[0-9])\.?){4}$/.test(ip);
}

function is_valid_mac_addr(mac) {
  return /^([\d[A-F]{2}:){5}[\d[A-F]{2}$/.test(mac);
}

function is_empty(str){
    if(str == null || str == ""){
        return true
    }
    return false
}

function create_script() {
    $.ajax({
        url: "http://127.0.0.1:8000/get_script",
        type: "POST"
    });
}

jsPlumb.ready(function () {
    var sw_id=1;
    var ht_id=1;
    var count_id=1;
    var dialog;
    dialog = $("#dialog-node").dialog({
        autoOpen: false,
        height: 350,
        width: 250,
        modal: true,
        buttons: [
            {
                text: "save",
                click: function () {
                    var name = $("#name").val();
                    var ip = $("#ip").val();
                    var mac = $("#mac").val();
                    if (!is_empty(ip) && !is_valid_ipv4_addr(ip)){
                        alert("invalid ip address");
                        return false
                    }
                    if (!is_empty(mac) && !is_valid_mac_addr(mac)){
                        alert("invalid mac address");
                        return false
                    }
                    if (is_empty(name)) {
                        alert("name can`t be empty");
                        return false
                    }
                    var node_id = $(this).dialog("option", "param");
                    $("#" + node_id).text("");
                    $("#" + node_id).append("<div class=\"ep\"></div>" + name);
                    $.ajax({
                        url: "http://127.0.0.1:8000/set_node_label",
                        type: "POST",
                        data: {"id": node_id,
                            "label": name,
                            "mac": mac,
                            "ip": ip
                        },
                        dataType: "text"
                    });
                    $(this).dialog("close");
                    return true
                }
            },
            {
                text: "cancel",
                click: function () {
                    $(this).dialog("close");
                }
            }
        ]
    });

    function is_int(x) {
        return x % 1 === 0;
    }


    var dialog1;
    dialog1 = $("#dialog-connection").dialog({
        autoOpen: false,
        height: 490,
        width: 270,
        modal: true,
        buttons: [
            {
                text: "save",
                click: function () {
                    var name = $("#con_name").val();
                    var con_loss = $("#con_loss").val();
                    var queue = $("#queue").val();
                    if (is_empty(name)) {
                        alert("name can`t be empty");
                        return false
                    }
                    if (!is_empty(con_loss) && !is_int(con_loss)) {
                        alert("loss should be integer");
                        return false
                    }
                    if (!is_empty(queue) && !is_int(queue)) {
                        alert("queue should be integer");
                        return false
                    }
                    var con = $(this).dialog("option", "param");
                    con.getOverlay("label").setLabel(name)
                    $.ajax({
                        url: "http://127.0.0.1:8000/set_connection_info",
                        type: "POST",
                        data: {"id": con.id,
                            "label": name,
                            "loss": con_loss,
                            "queue": queue
                        },
                        dataType: "text"
                    });
                    $(this).dialog("close");
                }
            },
            {
                text: "cancel",
                click: function () {
                    $(this).dialog("close");
                }
            }
        ]
    });

    var instance = jsPlumb.getInstance({
        Endpoint: ["Dot", {
            radius: 2
        }],
        HoverPaintStyle: {
            strokeStyle: "#1e8151",
            lineWidth: 2
        },
        ConnectionOverlays: [
            [ "Label", {id: "label", cssClass: "aLabel" }],
        ],
        Container: "map"
    });

    $("#menu .static_block").draggable({
        helper: "clone",
        appendTo: "#trash"
    });

    $("#menu .static_block_switch").draggable({
        helper: "clone",
        appendTo: "#trash"
    });

    instance.bind("dblclick", function (c) {
        $.ajax({
            url: "http://127.0.0.1:8000/delete_connection",
            type: "POST",
            data: {"id": c.id
            },
            dataType: "text"
        });
        instance.detach(c);
    });

    instance.bind("contextmenu", function (component, originalEvent) {
        dialog1.dialog("option", 'param', component)
        dialog1.dialog("open")
    });

    instance.bind("connection", function (info) {
        $.ajax({
            url: "http://127.0.0.1:8000/new_connection",
            type: "POST",
            data: {"id": info.connection.id,
                "node1": info.target.id,
                "node2": info.source.id
            },
            dataType: "text"
        });
        info.connection.getOverlay("label").setLabel(info.connection.id);
    });

    $("#trash").droppable({
        accept: "#menu .static_block, #menu .static_block_switch",
        drop: function (event, ui) {
            var element = ui.helper.clone();
            var type;
            ui.helper.remove();

            element.dblclick(function () {
                instance.detachAllConnections(this.id)
                $.ajax({
                    url: "http://127.0.0.1:8000/delete_node",
                    type: "POST",
                    data: {"id": this.id
                    },
                    dataType: "text"
                });
                $(this).remove();
            });

            element.contextmenu(function () {
                dialog.dialog("option", 'param', this.id)
                dialog.dialog("open")
            });

            if (element.attr("class") == "static_block_switch ui-draggable ui-draggable-dragging"){
                element.removeAttr("class");
                element.addClass("w_switch");
                type = "switch";
                count_id = sw_id;
                sw_id++;
            }
            else{
                element.removeAttr("class");
                element.addClass("w");
                type = "host";
                count_id = ht_id;
                ht_id++;
            }
            element.appendTo("#trash");

            instance.draggable(element);

            element.draggable({
                containment: "#trash"
            });

            $("#" + element.attr("id")).text("");
            $("#" + element.attr("id")).append("<div class=\"ep\"></div>" + type + "_" + count_id);


            instance.makeSource(element, {
                filter: ".ep",
                anchor: "Continuous",
                connector: ["StateMachine", {
                    curviness: 20
                }],
                connectorStyle: {
                    strokeStyle: "#5c96bc",
                    lineWidth: 2,
                    outlineColor: "transparent",
                    outlineWidth: 4
                }
            });
            instance.makeTarget(element, {
                anchor: "Continuous",
                allowLoopback: true
            });

            $.ajax({
                  url: "http://127.0.0.1:8000/new_node",
                  type: "POST",
                  data: {"id": element.attr("id"),
                         "name": element.text(),
                         "type": type
                  },
                  dataType: "text"
            });
        }
    })
});