from backend.common.db_connector import Base, db_session

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship

from datetime import datetime


class Baremetal(Base):
    __tablename__ = 'broker_baremetal'
    id = Column(Integer, primary_key=True, autoincrement=True)
    public_ip = Column(String(16), nullable=False)

    def __init__(self, public_ip):
        self.public_ip = public_ip

    @classmethod
    def get_or_create(cls, public_ip):
        re = cls.query.filter_by(public_ip=public_ip).first()
        if re is None:
            b = Baremetal(public_ip)
            db_session.add(b)
            db_session.commit()
            return b
        return re


class Broker(Base):
    __tablename__ = 'broker_brokers'
    id = Column(String(100), primary_key=True)
    container_id = Column(String(100), nullable=False)
    port = Column(Integer, nullable=False)
    created = Column(DateTime, nullable=False)
    baremetal_id = Column(Integer, ForeignKey(Baremetal.id))
    scaled = Column(Integer, nullable=False, default=0)

    baremetal = relationship("Baremetal", back_populates="brokers")

    def __init__(self, id, container_id, public_ip, port, host=None):
        self.id = id
        self.container_id = container_id
        self.public_ip = public_ip
        self.port = port
        self.created = datetime.now()
        self.baremetal = host

Baremetal.brokers = relationship("Broker", back_populates="baremetal")
