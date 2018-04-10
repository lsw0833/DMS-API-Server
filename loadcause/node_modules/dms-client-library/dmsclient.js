var mqtt = require('mqtt');
var proper = require('./proper');
class Dmsclient {
  constructor(address, topic) {
    this.client = null;
    this.p = new proper(address);
    this.p.isProperTopic(topic, (flag) => {
      if (flag) {
        this.apiTopic = topic;
      } else {
        console.log("Error : please check your topic!");
        process.exit(1);
      }
    });
  }
  connect(callback) {
    this.p.getIP((ip) => {
      var flag = false;
      var real = "tcp://" + ip.ip;
      this.client = mqtt.connect(real);
      this.client.subscribe("broadcast");
      callback(ip.ip);
    });
  }
  basicConnect(ip,callback){
    var real = "tcp://" + ip;
    this.client = mqtt.connect(real);
    this.client.subscribe("broadcast");
    callback(ip);
  }
  publish(topic, payload, callback) {
    let realTopic = this.apiTopic + "/" + topic;
    this.client.publish(realTopic, payload);
    callback(null);
  }
  subscribe(topic, callback) {
    let realTopic = this.apiTopic + "/" + topic;
    this.client.subscribe(realTopic);
    callback(null);
  }
  unsubscribe(topic, callback) {
    let realTopic = this.apiTopic + "/" + topic;
    this.client.unsubscribe(realTopic);
    callback(null);
  }
  packetArrived(doing, callback) {
    this.client.on('message', (topic, message) => {
      doing(topic, message);
    });
    callback(null);
  }
  disconnet(callback) {
    this.client.end();
    callback(null);
  }
}
module.exports = Dmsclient;
