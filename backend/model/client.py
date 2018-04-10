from backend.model.broker import Broker
from backend.common.db_connector import Base, db_session

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship


class Client(Base):
    __tablename__ = 'client_clients'
    id = Column(Integer, primary_key=True, autoincrement=True)
    client_mqtt_id = Column(String(1024), nullable=False)
    last_connected = Column(DateTime, nullable=False)
    brokers_id = Column(String(100), ForeignKey(Broker.id))

    broker = relationship("Broker", back_populates="clients")

    def __init__(self, client_mqtt_id, last_connected, broker):
        self.client_mqtt_id = client_mqtt_id
        self.last_connected = last_connected
        self.broker = broker

    @classmethod
    def get_by_client_mqtt_id(cls, client_mqtt_id):
        c = Client.query.filter_by(client_mqtt_id=client_mqtt_id).first()
        return c

    @classmethod
    def get_by_broker_id(cls, broker_id):
        c = Client.query.filter_by(brokers_id=broker_id)
        return c


Broker.clients = relationship("Client", back_populates="broker")

