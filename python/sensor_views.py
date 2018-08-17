from flask import Flask, request, jsonify
# from flask_cors import CORS
# from flask_jwt_extended import JWTManager
import creds
import json
import sensor_data as sensors
from init import app, jwt
from flask_jwt_extended import jwt_required, \
    get_jwt_identity, get_jwt_claims

app.secret_key = creds.jwt_secret

# Sensor data routes ####################################
@app.route("/data", methods=['POST',])
@jwt_required
def update_data():
    '''
    Writes data to influx from remote sensor
    '''
    # print request.headers
    allowed = ['sensor', 'python']
    if get_jwt_claims()['role'] in allowed:
        content = request.get_json(silent=False)
        # print content
        return jsonify(sensors.write_data(content)), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403

@app.route("/data", methods=['GET',])
@jwt_required
def get_data():
    '''
    Get data from influx about sensor types
    returns: [{'site': 'marcus',
        'location': [{'fields': [u'light', u'temp'], 'id': u'downhall'},
                    {'fields': [u'light', u'temp'], 'id': u'kitchen'},
                    {'fields': [u'light', u'temp'], 'id': u'lounge'},
                    {'fields': [u'light', u'temp'], 'id': u'spare'},
                    {'fields': [u'light', u'temp'], 'id': u'window'}]}]
    '''
    # print request.headers
    allowed = ['admin', 'sensuser']
    if get_jwt_claims()['role'] in allowed:
        return jsonify({"sensorID": sensors.get_sensorIDs(), "measurements": sensors.get_measurements()}), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403

@app.route("/data/values", methods=['POST',])
@jwt_required
def get_values():
    '''
    Get data from influx
    sends: {"measurement": [{"location": <location1>, "sensors":[{'id': <sens1>, 'type': <temp/hum>}........]},....], "range":<RP to graph from>, "period": int}
    returns: traces for plotly
    '''
    # print request.headers
    allowed = ['admin', 'sensuser']
    if get_jwt_claims()['role'] in allowed:
        content = request.get_json(silent=False)
        # print 'views content is:'
        # print content
        return jsonify(sensors.start_data(content)), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403

@app.route("/data/values/custom", methods=['POST',])
@jwt_required
def get_cust_values():
    '''
    Get data from influx
    sends: {"measurement": [{"location": <location1>, "sensors":[{'id': <sens1>, 'type': <temp/hum>}........]},....], "range":<RP to graph from>, "period": int}
    returns: traces for plotly
    '''
    # print request.headers
    allowed = ['admin', 'sensuser']
    if get_jwt_claims()['role'] in allowed:
        content = request.get_json(silent=False)
        # print 'views content is:'
        # print content
        return jsonify(sensors.custom_data(content)), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403

@app.route("/data/values", methods=['GET',])
@jwt_required
def get_sites():
    '''
    Get a list of sites
    '''
    # print request.headers
    allowed = ['admin', 'sensuser']
    if get_jwt_claims()['role'] in allowed:
        content = request.get_json(silent=False)
        # print 'views content is:'
        # print content
        return jsonify(sensors.get_sites()), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403

@app.route("/data/values/site/<site>", methods=['GET',])
@jwt_required
def get_site_data(site):
    '''
    Get a site data keys
    '''
    # print request.headers
    allowed = ['admin', 'sensuser']
    if get_jwt_claims()['role'] in allowed:
        # content = request.get_json(silent=False)
        # print 'views content is:'
        # print content
        return jsonify(sensors.get_sensorIDs(site)), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403

@app.route("/data/values/type/<Type>", methods=['GET',])
@jwt_required
def get_type_data(Type):
    '''
    Get a sensor type data keys
    '''
    # print request.headers
    allowed = ['admin', 'sensuser']
    if get_jwt_claims()['role'] in allowed:
        content = request.get_json(silent=False)
        # print 'views content is:'
        # print content
        return jsonify(sensors.get_type_sensors(Type)), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403

@app.route("/data/values/all", methods=['GET',])
@jwt_required
def get_all_sens():
    '''
    Get a sensor type data keys
    '''
    # print request.headers
    allowed = ['admin', 'sensuser']
    if get_jwt_claims()['role'] in allowed:
        content = request.get_json(silent=False)
        # print 'views content is:'
        # print content
        return jsonify(sensors.get_all_sensors()), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403

if __name__ == "__main__":
    app.run()
