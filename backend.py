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
import threading

Base = declarative_base()

import gps

gpsd = None #seting the global variable
gpsp = None

class GpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    global gpsd #bring it in scope
    gpsd = gps.gps(mode=gps.WATCH_ENABLE) #starting the stream of info
    self.current_value = None
    self.running = True #setting the thread running to true

  def run(self):
    global gpsd
    while gpsp.running:
      gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer

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
    rel_throttle = interface.get_rel_throttle()
    abs_throttle_b = interface.get_abs_throttle_b()
    acc_pedal_d = interface.get_acc_pedal_d()
    acc_pedal_e = interface.get_acc_pedal_e()

    #gpsdata = gpssession.next()
    #print gpsd.utc
    #print gpsd.fix.latitude
    #print gpsd.fix.longitude
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
                           rel_throttle=rel_throttle,
                           abs_throttle_b=abs_throttle_b,
                           acc_pedal_d=acc_pedal_d,
                           acc_pedal_e=acc_pedal_e,
                           gps_altitude=gpsd.fix.altitude,
                           gps_lat=gpsd.fix.latitude,
                           gps_long=gpsd.fix.longitude,
                           gps_speed=gpsd.fix.speed,
                           gps_climb=gpsd.fix.climb,
                           gps_track=gpsd.fix.track,
                           gps_mode=gpsd.fix.mode,
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

    #gpssession = gps.gps()
    #gpssession.stream(gps.WATCH_ENABLE|gps.WATCH_NEWSTYLE)
    global gpsp
    gpsp = GpsPoller() # create the thread
    gpsp.start()

    try:
        while 1:
            record = poll(interface)
            s.add(record)
            s.commit()
            #time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
            gpsp.running = False
            gpsp.join() # wait for the thread to finish what it's doing


if __name__ == "__main__":
    main()
