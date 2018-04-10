var request = require('request');
class Proper {
  constructor(address){
    this.address = address;
  }
  getIP(callback){
    var options = {
      url: 'http://'+ this.address +'/proper',
      method:'GET',
      headers:this.headers,
      json: true
    };

    request(options, (err,res,body) => {
      callback(body);
    });
  }
  isProperTopic(topic,callback){
    var options = {
      url: 'http://'+ this.address +'/isProper',
      method:'POST',
      headers:this.headers,
      json: true,
      form : {topic : topic}
    };
    request(options, (err,res,body) => {
      if(body.flag == false){
        callback(false);
      }else{
        callback(true);
      }
    });
  }
}
module.exports = Proper;
