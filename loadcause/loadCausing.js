var dmsclient = require('dms-client-library');
var dms = new dmsclient("163.180.117.30:8080","testTopic");
dms.connect((ip) => {
  setInterval(() => {
    dms.publish("test","This is a test!",(flag)=>{
    });
  }, 25);
});
