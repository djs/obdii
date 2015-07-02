from flask import Flask
from flask import render_template
from flask import url_for
from flask import json
from flask import request
from flask.ext.sqlalchemy import SQLAlchemy

import elm
import test_elm
import obdii

import random
random.seed()

import schema

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///live.sqlite'
db = SQLAlchemy(app)


class ObdiiSim(obdii.Obdii):
    def get_current_engine_rpm(self):
        return random.randint(600, 4000)
    def get_throttle_position(self):
        return random.randint(0, 100)
    def get_vehicle_speed(self):
        return random.randint(0, 120)



elm_interface = elm.Elm(test_elm.MockElm327())
#interface = obdii.Obdii(elm_interface)
interface = ObdiiSim(elm_interface)

@app.route("/")
def home():
    return render_template('home.html')

@app.route('/api/engine/speed')
def engine_speed():
    #x = interface.get_current_engine_rpm()
    x = db.session.query(schema.Record).order_by(schema.Record.id.desc()).first()
    return json.jsonify(speed=x.speed)

@app.route('/api/engine')
def engine():
    #rpm = interface.get_current_engine_rpm()
    #throttle = interface.get_throttle_position()
    x = db.session.query(schema.Record).order_by(schema.Record.id.desc()).first()
    return json.jsonify(rpm=x.rpm,
                        throttle=x.throttle,
                        maf=x.maf,
                        ect=x.ect,
                        fuel_rate=x.fuel_rate,
                        fuel_pressure=x.fuel_pressure,
                        timestamp=x.timestamp)

@app.route('/api/vehicle')
def vehicle():
    #speed = interface.get_vehicle_speed()
    x = db.session.query(schema.Record).order_by(schema.Record.id.desc()).first()
    return json.jsonify(speed=x.speed,
                        barometric_pressure=x.pressure,
                        ambient=x.intake_temp,
                        timestamp=x.timestamp)

@app.route('/api/ports')
def ports():
    return json.jsonify(ports=elm.available_ports())

@app.route('/api/event/update', methods=['POST'])
def event_update():
    data = request.get_json()


def elm_initialize():
    pass


if __name__ == "__main__":
    elm_initialize()
    app.run(debug=True)
