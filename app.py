from flask import Flask
from flask import render_template
from flask import url_for
from flask import json

import elm
import test_elm
import obdii

import random
random.seed()

app = Flask(__name__)

class ObdiiSim(obdii.Obdii):2
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
    x = interface.get_current_engine_rpm()
    return json.jsonify(rpm=x)

@app.route('/api/engine')
def engine():
    rpm = interface.get_current_engine_rpm()
    throttle = interface.get_throttle_position()
    #throttle = 0
    return json.jsonify(rpm=rpm, throttle=throttle)

@app.route('/api/vehicle')
def vehicle():
    speed = interface.get_vehicle_speed()
    return json.jsonify(speed=speed)

@app.route('/api/ports')
def ports():
    return json.jsonify(ports=elm.available_ports())

def elm_initialize():
    pass


if __name__ == "__main__":
    elm_initialize()
    app.run(debug=True)
