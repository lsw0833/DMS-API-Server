from backend import app
import pymysql
from flask import jsonify,request

@app.route('/getTopic', methods=['GET'])
def get_topic_list():
    conn = pymysql.connect(host='localhost', user='root', password='dms123', db='dmsDB')
    curs = conn.cursor()
    sql = 'select topic from client_topic'
    curs.execute(sql)
    result = curs.fetchall()
    t_list = []
    for topic in result:
        t_list.append(topic[0])
    conn.close()
    return jsonify({"list": t_list })

@app.route('/topic', methods=['POST'])
def add_topic():
    conn = pymysql.connect(host='localhost', user='root', password='dms123', db='dmsDB')
    curs = conn.cursor()
    data = request.get_json()
    topic = str(data['topic'])
    sql = "select topic from client_topic where topic='%s'" % (topic)
    curs.execute(sql)
    result = curs.fetchall()
    if len(result) != 0:
        conn.close()
        return "The same topic exists."
    sql = "insert into client_topic(topic) values ('%s')"% (topic)
    curs.execute(sql)
    conn.commit()
    conn.close()
    return "success"


@app.route('/topic', methods=['DELETE'])
def remove_topic():
    conn = pymysql.connect(host='localhost', user='root', password='dms123', db='dmsDB')
    curs = conn.cursor()
    data = request.get_json()
    topic = str(data['topic'])
    sql = "select topic from client_topic where topic='%s'" % (topic)
    curs.execute(sql)
    result = curs.fetchall()
    if len(result) == 0:
        conn.close()
        return "The topic you are trying to delete does not exist."
    sql = "delete from client_topic where topic = '%s'" %(topic)
    curs.execute(sql)
    conn.commit()
    conn.close()
    return "success"

@app.route('/isProper', methods=['POST'])
def is_proper_topic():
    conn = pymysql.connect(host='localhost', user='root', password='dms123', db='dmsDB')
    curs = conn.cursor()
    data = request.form['topic']
    topic = str(data)
    slashIdx = topic.find("/")
    if slashIdx != -1:
        topic = topic[0:slashIdx]
    sql = "select topic from client_topic where topic='%s'" % (topic)
    curs.execute(sql)
    result = curs.fetchall()
    proper = True
    conn.close()
    if len(result) == 0:
        proper=False
    return jsonify(flag=proper)
