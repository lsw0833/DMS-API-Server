# -*- coding: utf-8 -*-
from backend.config import DB_HOST

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(DB_HOST, convert_unicode=True,
                       pool_recycle=3600)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))


class DBase(object):
    def as_dict(self):
        return dict((c.name, getattr(self, c.name)) for c in self.__table__.columns)


Base = declarative_base(cls=DBase)
Base.query = db_session.query_property()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import backend.model
    Base.metadata.create_all(bind=engine)
