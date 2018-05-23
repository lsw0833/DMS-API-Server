from backend import app
from backend.model.broker import Broker, Baremetal
from backend.model.client import Client
from backend.common.db_connector import db_session
from backend.model.resources import get_broker_lastest_resource
from backend.model.resources import Setting

from flask import jsonify, request
import time
import subprocess
from datetime import timedelta

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/admin/brokers', methods=['GET'])
def get_broker_list_for_admin():
    brokers = Broker.query.order_by(Broker.created).all()
    cpu = Setting.query.filter_by(id='cpu').first()
    result = []
    result.append(cpu.value) 
    for broker in brokers:
        b = broker.as_dict()
        cpu, network_in, network_out, ts = get_broker_lastest_resource(b['id'])
        b['cpu'] = cpu
        b['network_in'] = network_in
        b['network_out'] = network_out
        b['last_check'] = ts
        client = Client.get_by_broker_id(b['id'])
        b['clients'] = len([c for c in client])
	result.append(b)

    return jsonify(brokers=result)


@app.route('/brokers', methods=['GET'])
def get_broker_list():
    baremetals = Baremetal.query.all()
    brokers = list()

    for baremetal in baremetals:
        d = dict()
        d['ip'] = baremetal.public_ip
        d['port'] = list()
        for b in baremetal.brokers:
            d['port'].append(b.port)
        d['port'].sort()
        brokers.append(d)
    return jsonify(hosts=brokers)


@app.route('/proper', methods=['GET'])
def get_proper_broker():
    broker = Broker.query.filter_by(scaled=0).first()
    baremetal = Baremetal.query.filter_by(id=broker.baremetal_id).first()
    ip = baremetal.public_ip
    port = broker.port
    result = ip+":"+str(port)
    return jsonify(ip=result)

@app.route('/hosts', methods=['POST'])
def add_host():
    data = request.get_json()
    ret = Baremetal.get_or_create(data['public_ip'])
    if ret is None:
        return 'Error', 500
    return '', 200


@app.route('/brokers', methods=['POST'])
def add_broker():
    data = request.get_json()
    baremetal = Baremetal.query.filter_by(public_ip=data['host']).first()

    if baremetal is None:
        return "Host doesn't existed", 404

    broker = Broker(data['broker_id'], data['container_id'], data['host'],
                    data['port'], baremetal)
    db_session.add(broker)
    db_session.commit()
    return ''


@app.route('/brokers/<broker_id>', methods=['DELETE'])
def delete_broker(broker_id):
    broker = Broker.query.filter_by(id=broker_id).first()
    if broker is None:
        return 'Broker id does not exist', 404
    db_session.delete(broker)
    db_session.commit()
    return ''

@app.route('/admin/baremetal', methods=['POST'])
def add_baremetal():
    data = request.get_json()
    ip = data['ip']
    baremetal = Baremetal(data['ip'])
    db_session.add(baremetal)
    db_session.commit()
    return 'success'

@app.route('/startTools', methods=['POST'])
def start_tools():
    broker = Broker.query.filter_by(scaled=0).first()
    baremetal = Baremetal.query.filter_by(id=broker.baremetal_id).first()
    ip = baremetal.public_ip
    id = broker.container_id
    name = broker.id
    subprocess.Popen('python ./tools/monitor.py ' + ip + ' ' + id + ' ' + name + '&',shell=True)
    subprocess.Popen('python ./tools/autoscaler.py ' + id + ' ' + name+ ' &',shell=True)
    return ''
