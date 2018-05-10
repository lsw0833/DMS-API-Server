 setInterval(load_brokers, 1000);
 setInterval(load_client, 1000);



function load_brokers() {
    $.ajax({
        type: "GET",
        url: "/admin/brokers",
        success: function(data) {
            var content = "<tr><td>브로커 ID</td><td>컨테이너 ID</td>"+
            "<td>포트 번호</td><td>생성 시각</td><td>접속 수</td>" +
            "<td>CPU(%)</td>" +
            "<td>Network In(bytes/s)</td><td>Network Out(bytes/s)</td><td>Last Check</td></tr>";

            var brokers = data['brokers'];
	    var cpu = brokers[0];
            for(var k = 1 ; k < brokers.length; k++) {
                var b = brokers[k];
                var d;
                if(Number(b.cpu) >= Number(cpu)){
                    d = "<tr bgcolor='red'>";
                }else if(Number(b.cpu) < Number(cpu) && Number(b.cpu) >= Number(cpu)*0.8){
                    d = "<tr bgcolor='yellow'>";
                }
                else {
                    d = '<tr>';
                }
                d += "<td>"+b.id.slice(0,9)+"</td>";
                d += "<td>"+b.container_id.slice(0,9)+"</td>";
                d += "<td>"+b.port+"</td>";
                d += "<td>"+b.created+"</td>";
                d += "<td>"+b.clients+"</td>";
                d += "<td>"+b.cpu+"</td>";
                d += "<td>"+b.network_in+"</td>";
                d += "<td>"+b.network_out+"</td>";
                //d += "<td>"+b.last_check+"</td></tr>";
                var check = b.last_check;
                var year = Number(check.slice(0,4));
                var month = Number(check.slice(5,7))-1;
                var day = Number(check.slice(8,10));
                var hour = Number(check.slice(11,13))+9;
                var min = Number(check.slice(14,16));
                var sec = Number(check.slice(17,19));
                var time = new Date(year,month,day,hour,min,sec);
                d+="<td>"+time.toString()+"</td>";
                content += d;
            }

            $("#broker_list").html(content)
        }
    });
}
function load_client() {
     $.ajax({
        type: "GET",
        url: "/admin/clients",
        success: function(data) {
            var content = "<tr><td>클라이언트 ID</td><td>브로커 ID</td>"+
            "<td>최근 연결 시간</td</tr>";

            var clients = data['clients'];
            for(var k = 0 ; k < clients.length; k++) {
                var c = clients[k];
                var d ="<tr>";
                d += "<td>"+c.client_mqtt_id+"</td>";
                d += "<td>"+c.brokers_id.slice(0,9)+"</td>";
                //d += "<td>"+c.last_connected+"</td></tr>";
                var time = new Date(c.last_connected);
                d+= "<td>"+time.toString()+"</td></tr>";
                content += d;
            }

            $("#client_list").html(content)
            $("#client_count").html("클라이언트 목록 ("+clients.length+")")
        }
    });
}


function send_message() {
    var clients = [];
    var topic = document.getElementById('msg_topic').value;
    var body = document.getElementById('msg_body').value;


    $("input:checkbox[name=client]:checked").each(function(){
        var id = $(this).val();
        var bid = document.getElementById(id).innerText;
        var client = {'client_id': id, 'broker_id': bid};
        clients.push(client);
    });

    req_body = {'clients': clients, 'topic': topic, 'msg': body};

    $.ajax({
        type: "POST",
        data: JSON.stringify(req_body),
        contentType: 'application/json',
        url: '/send_message',
        success: function (msg) {
            alert(msg)
        }
    });

    document.getElementById('msg_topic').value = "";
    document.getElementById('msg_body').value = "";
}


function get_autoscale_setting() {
    $.ajax({
        type: "GET",
        url: '/admin/setting',
        success: function (msg) {
            var cpu = msg['cpu'];
            var period = msg['period'];

            document.getElementById('cpu_threshold').value = cpu;
            document.getElementById('threshold_period').value = period;
        }
    });
}


function autoscale_setting() {
    var cpu = document.getElementById('cpu_threshold').value;
    var period = document.getElementById('threshold_period').value;

    req_body = {'cpu': cpu, 'period': period};
    $.ajax({
        type: "POST",
        data: JSON.stringify(req_body),
        contentType: 'application/json',
        url: '/admin/setting',
        success: function (msg) {
            alert(msg);
        }
    });
}

function abort_test() {
    $.ajax({
        type: "GET",
        url: '/admin/test/stop',
        success: function (msg) {
            alert(msg);
            window.location.reload();
        }
    });
}

function start_test() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', 'http://163.180.117.110:5000/reset');


    $.ajax({
        type: "GET",
        url: '/admin/test/start',
        success: function (msg) {
            alert(msg);
            window.location.reload();
        }
    });

}

function delete_clients() {
    $("input:checkbox[name=client]").each(function(){
        var id = $(this).val();
        req_body = {'client_mqtt_id': id}
        $.ajax({
            type: "DELETE",
            data: JSON.stringify(req_body),
            contentType: 'application/json',
            url: '/client',
            success: function() {
                var content = "<tr><td>선택</td><td>클라이언트 ID</td>"+
                "<td>브로커 ID</td><td>최근 연결 시간</td></tr>"
                $("#client_list").html(content)
            }
        });
    });
}
function baremetal_add() {
    var ip = document.getElementById('public_ip').value;

    req_body = {'ip': ip };
    $.ajax({
        type: "POST",
        data: JSON.stringify(req_body),
        contentType: 'application/json',
        url: '/admin/baremetal',
        success: function (msg) {
            alert(msg);
        }
    });
     document.getElementById('public_ip').value = "";
}

function broadcast_msg() {
    var msg = document.getElementById('b_msg').value;

    req_body = {'msg': msg };
    $.ajax({
        type: "POST",
        data: JSON.stringify(req_body),
        contentType: 'application/json',
        url: '/admin/broadcast',
        success: function (msg) {
            alert(msg);
        }
    });
     document.getElementById('b_msg').value = "";
}
function get_topic_list() {
    $.ajax({
        type: "GET",
        url: "/getTopic",
        success: function(data) {
            var content = "<tr><th>-Topic List-</th></tr>";
            var topic = data['list'];
            if(topic.length == 0){
                content = "<tr><th>발행된 토픽이 없습니다.</th></tr>";
            }else{
                for(var i = 0 ; i < topic.length; i++) {
                    content += '<tr>';
                    content += "<td>"+topic[i]+"</td></tr>";
                }
            }
            $("#topic_list").html(content)
        }
    });
}

function topic_add() {
    var topic = document.getElementById('topic_input').value;
    req_body = {'topic': topic };
    $.ajax({
        type: "POST",
        data: JSON.stringify(req_body),
        contentType: 'application/json',
        url: '/topic',
        success: function (msg) {
            alert(msg);
        }
    });
     document.getElementById('topic_input').value = "";
}

function topic_delete() {
    var topic = document.getElementById('topic_input').value;

    req_body = {'topic': topic };
    $.ajax({
        type: "DELETE",
        data: JSON.stringify(req_body),
        contentType: 'application/json',
        url: '/topic',
        success: function (msg) {
            alert(msg);
        }
    });
     document.getElementById('topic_input').value = "";
}

function load_cause() {
    var cnt = document.getElementById('load_cnt').value;

    req_body = {'cnt': cnt };
    $.ajax({
        type: "POST",
        data: JSON.stringify(req_body),
        contentType: 'application/json',
        url: '/loadclient',
        success: function (msg) {
            alert(msg);
        }
    });
     document.getElementById('load_cnt').value = "";
}