#-*-coding: utf-8 -*-
import requests

from backend import app, config
from backend.model.broker import Broker , Baremetal
from backend.model.client import Client
from backend.common.db_connector import db_session

from flask import jsonify, request

from sqlalchemy import text
import pymysql
import MySQLdb
import random
import hashlib
from datetime import datetime
from docker import Client as DClient
import socket

import os
import subprocess

conn = pymysql.connect(host='localhost', user='root', password='dms123',db='dmsDB')
curs = conn.cursor()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/client', methods=['POST'])
def register_connected_client():
    data = request.get_json()
    client_mqtt_id = data['client_mqtt_id']
    last_connected = data['last_connected']
    broker_id = data['broker_id']

    broker = Broker.query.filter_by(id=broker_id).first()
    if broker is None:
        return 'Broker not found', 404

    client = Client.get_by_client_mqtt_id(client_mqtt_id)
    if client is None:
        client = Client(client_mqtt_id, last_connected, broker)
        db_session.add(client)
    else:
        client.brokers_id = broker_id
        client.last_connected = last_connected
    db_session.commit()
    return ''


@app.route('/admin/clients', methods=['GET'])
def get_connected_clients():
    clients = Client.query.all()
    return jsonify(clients=[c.as_dict() for c in clients])


@app.route('/get_id', methods=['POST'])
def get_clients_id():
    sql = 'select client_mqtt_id from client_clients order by last_connected desc limit 1'
    curs.execute(sql)
    result = curs.fetchall()
    res = str(result)
    rows = res.split('\'')
    print rows[1]
    return rows[1]


@app.route('/client', methods=['DELETE'])
def remove_disconnected_client():
    data = request.get_json()
    client_mqtt_id = data['client_mqtt_id']
    client = Client.query.filter_by(client_mqtt_id=client_mqtt_id)
    client = client.first()
    if client is None:
        return "Client doesn't exist", 404
    db_session.delete(client)
    db_session.commit()
    return ''


@app.route('/admin/test/stop', methods=['GET'])
def stop_test():
    os.system("ps -ef | grep autoscaler | awk '{print $2}' | xargs kill -9")
    os.system("ps -ef | grep loadCausing | awk '{print $2}' | xargs kill -9")
    os.system("ps -ef | grep brokermanager | awk '{print $2}' | xargs kill -9")
    Client.query.delete()
    Broker.query.delete()
    db_session.commit()
    cli = list()
    baremetals = Baremetal.query.all()
    for baremetal in baremetals:
        cli.append(DClient(base_url='tcp://'+baremetal.public_ip+':4243'))
    for i in range(0,len(cli)):
        containers = cli[i].containers()
        for c in containers:
            cli[i].remove_container(container=c['Id'],force=True)

    return '테스트 종료'

@app.route('/admin/test/start', methods=['GET'])
def start_test():
    localIPv4 = socket.gethostbyname(socket.getfqdn())
    subprocess.Popen('node ../brokermanager/brokermanager.js &', shell=True)
    sql = "select public_ip from broker_baremetal"
    db = MySQLdb.connect("127.0.0.1", "root", "dms123",
                         "dmsDB", charset='utf8')
    cursor = db.cursor()
    cursor.execute(sql)
    db.close()
    ip = str(cursor.fetchone()[0])
    sql = "select id from broker_baremetal"
    db = MySQLdb.connect("127.0.0.1", "root", "dms123",
                         "dmsDB", charset='utf8')
    cursor = db.cursor()
    cursor.execute(sql)
    db.close()
    id = int(cursor.fetchone()[0])
    cli = DClient(base_url='tcp://' + ip + ':4243')
    bid = hashlib.sha256(str(random.random()).encode()).hexdigest()  # docker container name
    port = 55500
    port2 = 45500
    c = cli.create_container(image='broker:0.1', detach=True, environment={
        'cluster': 'tcp://'+localIPv4+':1883',
        'brokerid': bid,
        'dbhost': localIPv4
    }, ports=[1883,3000], name=bid,
                             host_config=cli.create_host_config(
                                 port_bindings={
                                     1883: port,
				     3000: port2}))
    cli.start(container=c)

    sql = "insert into broker_brokers(id, container_id, port, created, " \
          "baremetal_id, scaled) values ('%s', '%s', '%d', '%s', '%d', 0)" \
          % (bid, c['Id'], port, datetime.now(), id)

    db = MySQLdb.connect("127.0.0.1", "root", "dms123",
                         "dmsDB", charset='utf8')
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()
    db.close()
    requests.post("http://127.0.0.1:8080/startTools")
    return '테스트 시작'

@app.route('/loadclient', methods=['POST'])
def load_client():
    data = request.get_json()
    cnt = int(data['cnt'])
    if cnt <= 0:
        return "check your input"
    for i in range(0,cnt):
        subprocess.Popen('node ./loadcause/loadCausing.js &', shell=True)
    return '생성 완료'
