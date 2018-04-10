<h1>DMS-Client-Library</h1>

DMS System을 이용할 클라이언트를 만들기 위한 Node.js API입니다.
<br>
<hr>
<h2>Install</h2>
<br>
npm install dms-client-library
<br>
<hr>
<h2>사용법</h2>
var dmsclient = require('dms-client-library');<br>
var dms = new dmsclient(address);<br>
모듈 require 후 객체생성후 사용<br>
address : DMS system이 실행되고있는 메인 서버의 IP:port
<br>
<br>
<h4>connect(callback)</h4><br>
클라이언트가 적절한 브로커에 연결됨
<br>
callback : function(ip){}<br>
ip : 적절한 브로커 ip를 담고있는 객체
<br>
<hr>
<h4>publish(topic, payload, callback)</h4><br>
클라이언트가 message를 publish 함
<br>
topic : 보내려는 message의 토픽<br>
payload : message payload<br>
※ mqtt프로토콜 참고<br>
<hr>
<h4>subscribe(topic, callback)</h4><br>
클라이언트가 message를 수신함<br>
topic : 수신할 message topic<br>
<hr>
<h4>packetArrived(doing, callback)</h4><br>
메시지가 수신될 시 실행되는 함수<br>
doing : function(topic,payload){} <br>
메시지가 수신될시 수행 할 함수 (사용자 정의)
<br><hr>
<h4>disconnet(callback)</h4><br>
연결 해제 <br>
