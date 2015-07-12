
import elm
import test_elm
import obdii
import sqlalchemy
import time
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func, Numeric
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
    rel_throttle = Column(Integer)
    abs_throttle_b = Column(Integer)
    acc_pedal_d = Column(Integer)
    acc_pedal_e = Column(Integer)
    gps_altitude = Column(Numeric)
    gps_lat = Column(Numeric)
    gps_long = Column(Numeric)
    gps_speed = Column(Numeric)
    gps_climb = Column(Numeric)
    gps_track = Column(Numeric)
    gps_mode = Column(Integer)
    timestamp = Column(DateTime)
