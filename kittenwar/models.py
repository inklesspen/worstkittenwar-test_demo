from sqlalchemy import (
    Column,
    Integer,
    LargeBinary,
    String,
    Unicode,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker

from zope.sqlalchemy import register

Base = declarative_base()


class Kitten(Base):
    __tablename__ = 'kittens'
    id = Column(Integer, primary_key=True)
    file_extension = Column(String(10), nullable=False)
    file_data = Column(LargeBinary, nullable=False)
    source_url = Column(String(120), nullable=False)
    credit = Column(Unicode(40), nullable=False)
    views = Column(Integer, nullable=False, default=0)
    votes = Column(Integer, nullable=False, default=0)


def includeme(config):
    # We'll configure the DB connection from this.
    settings = config.get_settings()

    # by including pyramid_tm here, it doesn't need to be in the ini file.
    config.include('pyramid_tm')

    # connect to the DB and make a sessionmaker
    engine = engine_from_config(settings, 'sqlalchemy.')
    maker = sessionmaker()
    # register the sessionmaker with the zope transaction manager
    # all sessions created from this will be hooked up
    register(maker)
    # and finally connect the session to the engine
    maker.configure(bind=engine)

    # Store the sessionmaker in the registry; this will come in handy for utils
    config.registry['db_sessionmaker'] = maker

    # Every request will have a db_session property. The first time
    # you use it, it creates a session, and then replaces the property
    # with that session.
    config.add_request_method(lambda request: maker(), 'db_session', reify=True)
