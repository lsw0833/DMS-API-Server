from backend import app
from backend.model.client import Client, Broker

from flask import render_template, request

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json


@app.route('/dashboard', methods=['GET'])
def dashboard_index():
    clients = Client.query.all()
    return render_template('group.html', clients=clients)

@app.route('/admin/broadcast', methods=['POST'])
def broadcast_msg():
    data = request.get_json()
    msg = data['msg']
    client = mqtt.Client()
    client.connect("127.0.0.1",1883)
    client.publish("broadcast",msg)
    return 'success'
