from docker import Client
from influxdb import InfluxDBClient

import json
import sys

if len(sys.argv) != 4:
    sys.exit(-1)
ip = sys.argv[1] 
id = sys.argv[2] 
name = sys.argv[3]

client = InfluxDBClient(host='127.0.0.1', port=8086, database='monitoring')

cli = Client(base_url='tcp://'+ip+':4243')

for stats in cli.stats(container=id, stream=True):

    stats = json.loads(stats.decode())
    usercpu_query = "select last(value) from usercpu where container_name='%s'" \
                    % name

    syscpu_query = "select last(value) from syscpu where container_name='%s'" \
                   % name

    netin_query = "select last(value) from network_inbound " \
                  "where container_name='%s'" % name

    netout_query = "select last(value) from network_outbound " \
                   "where container_name='%s'" % name

    p_usercpu = 0
    p_syscpu = 0
    p_network_in = 0
    p_network_out = 0

    try:
        p_usercpu = [n for n in client.query(query=usercpu_query)][0][0]['last']
        p_syscpu = [n for n in client.query(query=syscpu_query)][0][0]['last']
        p_network_in = [n for n in client.query(query=netin_query)][0][0]['last']
        p_network_out = [n for n in client.query(query=netout_query)][0][0]['last']
    except Exception as e:
        print(e)

    data = {'points': [{
                    'measurement': '',
                    'tags': {'container_name': name},
                    'fields': {'value': ''}
                }]
    }

    cpu = stats['cpu_stats']['cpu_usage']['total_usage']
    syscpu = stats['cpu_stats']['system_cpu_usage']
    cpu_percent = 0.0

    user_delta = cpu - p_usercpu
    sys_delta = syscpu - p_syscpu
    if sys_delta > 0.0 and user_delta > 0.0:
        cpu_percent = (user_delta / float(sys_delta)) * float(
            len(stats['cpu_stats']['cpu_usage']['percpu_usage'])) * 100.0

    rx = stats['networks']['eth0']['rx_bytes']
    tx = stats['networks']['eth0']['tx_bytes']

    delta_rx = rx - p_network_in if p_network_in != 0 else 0
    delta_tx = tx - p_network_out if p_network_out != 0 else 0

    m_list = {'usercpu': cpu, 'syscpu': syscpu,
              'cpu': cpu_percent, 'network_inbound': rx, 'network_outbound': tx,
              'network_tx': delta_tx, 'network_rx': delta_rx}

    for k, v in m_list.items():
        data['points'][0]['measurement'] = k
        data['points'][0]['fields']['value'] = v
        client.write(data, params={'db': 'monitoring'})






