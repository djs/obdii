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

import schema
import sys

Base = declarative_base()


def poll(interface):
    rpm = interface.get_current_engine_rpm()
    speed = interface.get_vehicle_speed()
    throttle = interface.get_throttle_position()
    ect = interface.get_current_ect()
    speed = interface.get_vehicle_speed()
    maf = interface.get_maf_airflow_rate()
    fuel = interface.get_fuel_level_input()
    pressure = interface.get_barometric_pressure()
    #fuel_rate = interface.get_engine_fuel_rate()
    fuel_rate = 0
    intake_temp = interface.get_intake_air_temperature()
    #fuel_pressure = interface.get_fuel_pressure()
    fuel_pressure = 0
    record = schema.Record(rpm=rpm,
                           speed=speed,
                           throttle=throttle,
                           ect=ect,
                           maf=maf,
                           fuel=fuel,
                           pressure=pressure,
                           fuel_rate=fuel_rate,
                           intake_temp=intake_temp,
                           fuel_pressure=fuel_pressure,
                           timestamp=datetime.now())

    return record


def main():
    engine = create_engine('sqlite:///live.sqlite')
    Session = sessionmaker()
    Session.configure(bind=engine)
    schema.Base.metadata.create_all(engine)
    s = Session()

    if sys.argv[1] == 'mock':
        elm_interface = elm.Elm(test_elm.MockElm327())
    else:
        elm_interface = elm.Elm(sys.argv[1])
    interface = obdii.Obdii(elm_interface)

    while 1:
        record = poll(interface)
        s.add(record)
        s.commit()
        #time.sleep(1)


if __name__ == "__main__":
    main()
