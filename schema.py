
import elm
import test_elm
import obdii
import sqlalchemy
import time
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Record(Base):
    __tablename__ = 'records'
    id = Column(Integer, primary_key=True)
    rpm = Column(Integer)
    throttle = Column(Integer)
    speed = Column(Integer)
    ect = Column(Integer)
    maf = Column(Integer)
    fuel = Column(Integer)
    fuel_rate = Column(Integer)
    fuel_pressure = Column(Integer)
    intake_temp = Column(Integer)
    pressure = Column(Integer)
    timestamp = Column(DateTime)
