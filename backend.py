
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
    timestamp = Column(DateTime)


def poll(interface):
    rpm = interface.get_current_engine_rpm()
    speed = interface.get_vehicle_speed()
    throttle = interface.get_throttle_position()
    ect = interface.get_current_ect()
    speed = interface.get_vehicle_speed()
    maf = interface.get_maf_airflow_rate()
    fuel = interface.get_fuel_level_input()
    record = Record(rpm=rpm,
                    speed=speed,
                    throttle=throttle,
                    ect=ect,
                    maf=maf,
                    fuel=fuel,
                    timestamp=datetime.now())

    return record

def main():
    engine = create_engine('sqlite:///history.sqlite')
    Session = sessionmaker()
    Session.configure(bind=engine)
    Base.metadata.create_all(engine)
    s = Session()

    #elm_interface = elm.Elm(test_elm.MockElm327())
    elm_interface = elm.Elm('COM3')
    interface = obdii.Obdii(elm_interface)

    while 1:
        record = poll(interface)
        s.add(record)
        s.commit()
        #time.sleep(1)




if __name__ == "__main__":
    main()
