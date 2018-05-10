import MySQLdb
import time
import random
import hashlib
import sys
from datetime import datetime
from docker import Client
from influxdb import InfluxDBClient
import requests
import socket

if len(sys.argv) != 3:
    sys.exit(-1)

id = sys.argv[1]  # docker container id
name = sys.argv[2]  # docker container name

client = InfluxDBClient(host='127.0.0.1', port=8086, database='monitoring')

cpu = 0
period = 0


def get_settings():
    global cpu
    global period
    sql = "select value from settings where id='%s'"

    db = MySQLdb.connect("127.0.0.1", "root", "dms123",
                         "dmsDB", charset='utf8')

    cursor = db.cursor()
    cursor.execute(sql % 'cpu')
    cpu = cursor.fetchone()[0]

    cursor = db.cursor()
    cursor.execute(sql % 'period')
    period = cursor.fetchone()[0]
    db.close()


def count_connected_client():
    sql = "select count(id) from client_clients where brokers_id='%s'" % name
    db = MySQLdb.connect("127.0.0.1", "root", "dms123",
                         "dmsDB", charset='utf8')
    cursor = db.cursor()
    cursor.execute(sql)
    db.close()
    return int(cursor.fetchone()[0])


def inspect_broker_status():
    query = "select mean(value) from cpu where container_name='%s' " \
            "and time > now() - %ds" % (name, period)

    try:
        d = [c for c in client.query(query=query)][0][0]
    except Exception as e:
        return False

    value = d['mean']
    clients = count_connected_client()

    if value > cpu and clients > 0:
        return True
    return False


def get_proper_broker_host():
    sql = "select id from broker_baremetal"
    db = MySQLdb.connect("127.0.0.1", "root", "dms123",
                         "dmsDB", charset='utf8')
    cursor = db.cursor()
    cursor.execute(sql)
    db.close()
    id = cursor.fetchall()
    id_list = []
    for i in id:
        id_list.append(int(i[0]))
    cnt_list = []
    sql = "select count(id) from broker_brokers where baremetal_id = '%d'"
    for i in range(0, len(id_list)):
        db = MySQLdb.connect("127.0.0.1", "root", "dms123",
                             "dmsDB", charset='utf8')
        cursor = db.cursor()
        cursor.execute(sql % id_list[i])
        db.close()
        cnt = int(cursor.fetchone()[0])
        cnt_list.append(cnt)
    check = cnt_list[0]
    index = 0
    for i in range(0, len(cnt_list)):
        if check > cnt_list[i]:
            check = cnt_list[i]
            index = i

    sql = "select public_ip from broker_baremetal where id ='%d'" % id_list[index]
    db = MySQLdb.connect("127.0.0.1", "root", "dms123",
                         "dmsDB", charset='utf8')
    cursor = db.cursor()
    cursor.execute(sql)
    db.close()
    return str(cursor.fetchone()[0])


def get_baremetal_id(next_ip):
    sql = "select id from broker_baremetal where public_ip ='%s'" % next_ip
    db = MySQLdb.connect("127.0.0.1", "root", "dms123",
                         "dmsDB", charset='utf8')
    cursor = db.cursor()
    cursor.execute(sql)
    db.close()
    return int(cursor.fetchone()[0])


def get_last_port(next_ip):
    bare = get_baremetal_id(next_ip)
    sql = "select count(port) from broker_brokers where baremetal_id ='%d'" % bare
    db = MySQLdb.connect("127.0.0.1", "root", "dms123",
                         "dmsDB", charset='utf8')
    cursor = db.cursor()
    cursor.execute(sql)
    db.close()
    cnt = int(cursor.fetchone()[0])
    if cnt > 0:
        sql = "select port from broker_brokers where baremetal_id ='%d' order by port desc limit 1" % bare
        db = MySQLdb.connect("127.0.0.1", "root", "dms123",
                             "dmsDB", charset='utf8')
        cursor = db.cursor()
        cursor.execute(sql)
        db.close()
        return int(cursor.fetchone()[0])
    else:
        return 55499


def start_autoscaler_and_monitor():
    requests.post("http://127.0.0.1:8080/startTools")


def create_new_broker():
    localIPv4 = socket.gethostbyname(socket.getfqdn())
    next_ip = get_proper_broker_host()
    cli = Client(base_url='tcp://' + next_ip + ':4243')
    bid = hashlib.sha256(str(random.random()).encode()).hexdigest()  # docker container name
    port = get_last_port(next_ip) + 1
    port2 = port - 10000
    c = cli.create_container(image='broker:0.1', detach=True, environment={
        'cluster': 'tcp://' + localIPv4 + ':1883',
        'brokerid': bid,
        'dbhost': localIPv4
    },ports=[1883, 3000], name=bid,
                             host_config=cli.create_host_config(
                                 port_bindings={
                                     1883: port,
                                     3000: port2}))
    cli.start(container=c)

    sql = "insert into broker_brokers(id, container_id, port, created, " \
          "baremetal_id, scaled) values ('%s', '%s', '%d', '%s', '%d', 0)" \
          % (bid, c['Id'], port, datetime.now(), get_baremetal_id(next_ip))

    db = MySQLdb.connect("127.0.0.1", "root", "dms123",
                         "dmsDB", charset='utf8')
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()
    db.close()


def mark_as_scaled():
    sql = "update broker_brokers set scaled=1 where id='%s'" % name

    db = MySQLdb.connect("127.0.0.1", "root", "dms123",
                         "dmsDB", charset='utf8')
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()
    db.close()


def work():
    while True:
        get_settings()
        if inspect_broker_status():
            create_new_broker()
            mark_as_scaled()
            start_autoscaler_and_monitor()
            break;
        time.sleep(1)


if __name__ == '__main__':
    work()
