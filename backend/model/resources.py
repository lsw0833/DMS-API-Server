from influxdb import InfluxDBClient

from backend.common.db_connector import Base, db_session
from sqlalchemy import Column, Integer, String
from backend.config import InfluxDB_DBNAME, InfluxDB_HOST


def get_broker_lastest_resource(bid):
    client = InfluxDBClient(host=InfluxDB_HOST, port=8086,
                            database=InfluxDB_DBNAME)
    cpu_query = "select last(value), time from cpu where container_name='%s'" % bid

    netin_query = "select last(value), time from network_rx " \
                  "where container_name='%s'" % bid
    netout_query = "select last(value), time from network_tx where " \
                   "container_name='%s'" % bid

    cpu_l = [c for c in client.query(query=cpu_query)]
    try:
        cpu = format(cpu_l[0][0]['last'], '.4f')
    except Exception as e:
        return 0, 0, 0, 0

    ts = cpu_l[0][0]['time'].split('.')[0]
    network_in = [n for n in client.query(query=netin_query)][0][0]['last']
    network_out = [n for n in client.query(query=netout_query)][0][0]['last']
        
    return cpu, network_in, network_out, ts


class Setting(Base):
    __tablename__ = 'settings'
    id = Column(String(100), primary_key=True)
    value = Column(Integer, nullable=False)

    def __init__(self, key, value):
        self.id = key
        self.value = value

    @classmethod
    def create_or_update(cls, key, value):
        setting = Setting.query.filter_by(id=key).first()
        if setting is None:
            s = Setting(key, value)
            db_session.add(s)
        else:
            setting.value = value
        db_session.commit()
