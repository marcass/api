from flask import Flask, request, jsonify
import creds
import json
import sensor_data as sensors
from init import app

# Sensor data routes ####################################
@app.route("/data", methods=['POST',])
def update_data():
    '''
    Writes data to influx from remote sensor
    '''
    #print("SEnsor data incoming")
    # print (request.headers)
    content = request.get_json(silent=False)
    # print content
    return jsonify(sensors.write_data(content)), 200

@app.route("/data/tanks", methods=['POST',])
def update_data_tanks():
    '''
    Writes data to influx from tank remote sensor
    '''
    print("got tanks data")
    print (request.headers)
    #try:
    content = request.get_json(silent=False)
    print (content)
    #except:
    #    print("could not read data")
    return jsonify(sensors.sort_tank_data(content)), 200


# @app.route("/data/values/types", methods=['GET',])
# def get_data():
#     '''
#     Get data from influx about sensor types
#     returns: [{'site': 'marcus',
#         'location': [{'fields': [u'light', u'temp'], 'id': u'downhall'},
#                     {'fields': [u'light', u'temp'], 'id': u'kitchen'},
#                     {'fields': [u'light', u'temp'], 'id': u'lounge'},
#                     {'fields': [u'light', u'temp'], 'id': u'spare'},
#                     {'fields': [u'light', u'temp'], 'id': u'window'}]}]
#     '''
#     return jsonify({"sensorID": sensors.get_sensorIDs(), "measurements": sensors.get_measurements()}), 200


@app.route("/data/values", methods=['POST',])
def get_values():
    '''
    Get data from influx
    sends: {"measurement": [{"location": <location1>, "sensors":[{'id': <sens1>, 'type': <temp/hum>}........]},....], "range":<RP to graph from>, "period": int}
    returns: traces for plotly
    '''
    content = request.get_json(silent=False)
    # print 'views content is:'
    # print content
    return jsonify(sensors.start_data(content)), 200


@app.route("/data/values/custom", methods=['POST',])
def get_cust_values():
    '''
    Get data from influx
    sends: {"measurement": [{"location": <location1>, "sensors":[{'id': <sens1>, 'type': <temp/hum>}........]},....], "range":<RP to graph from>, "period": int}
    returns: traces for plotly
    '''
    content = request.get_json(silent=False)
    # print 'views content is:'
    # print content
    return jsonify(sensors.custom_data(content)), 200

@app.route("/data/values/customAx", methods=['POST',])
def get_cust_axes():
    '''
    Get data from influx
    sends: {"site": site, "traces": [{"senosorID": "lounge", "site": "julian", "type": "light"}, .....], "range":<RP to graph from>, "period": int}
    returns: traces for plotly
    '''
    content = request.get_json(silent=False)
    # print 'views content is:'
    # print content
    return jsonify(sensors.custom_ax(content)), 200

# @app.route("/data/values/sites", methods=['GET',])
# def get_sites():
#     '''
#     Get a list of sites
#     '''
#     # print request.headers
#     allowed = ['admin', 'sensuser']
#     user_data = get_jwt_claims()
#     if user_data['role'] in allowed:
#         sites = sensors.get_sites()
#         if user_data['role'] == 'admin':
#             ret = []
#             for i in sites[0]:
#                 loc = sites[0].index(i)
#                 ret.append({'sitename':sites[0][loc], 'measurement': sites[1][loc]})
#             return jsonify(ret), 200
#         # content = request.get_json(silent=False)
#         else:
#             if 'sites' in user_data:
#                 allowed_sites = []
#                 for i in user_data['sites']:
#                     allowed = json.loads(i)
#                     if allowed['sitename'] in sites[0]:
#                         loc = sites[0].index(allowed['sitename'])
#                         allowed_sites.append({'sitename':sites[0][loc], 'measurement':sites[1][loc]})
#                 return jsonify(allowed_sites), 200
#             else:
#                 jsonify({"msg": "Forbidden"}), 403

@app.route("/data/values/sites", methods=['GET',])
def get_sites():
    '''
    Get a list of sites
    '''
    sites = sensors.get_sites()
    # Need some way for kong to spit out user here, or change routes dynamically
    if user_data['role'] == 'admin':
        ret = []
        for i in sites[0]:
            loc = sites[0].index(i)
            ret.append({'sitename':sites[0][loc], 'measurement': sites[1][loc]})
        return jsonify(ret), 200
    # content = request.get_json(silent=False)
    else:
        if 'sites' in user_data:
            allowed_sites = []
            for i in user_data['sites']:
                allowed = json.loads(i)
                if allowed['sitename'] in sites[0]:
                    loc = sites[0].index(allowed['sitename'])
                    allowed_sites.append({'sitename':sites[0][loc], 'measurement':sites[1][loc]})
            return jsonify(allowed_sites), 200


@app.route("/data/values/types", methods=['GET',])
def get_types():
    '''
    Get a list of types
    '''
    return jsonify(sensors.get_data_types()), 200

@app.route("/data/values/site/<site>", methods=['GET',])
def get_site_data(site):
    '''
    Get a site data keys without specifying measurement
    '''
    return jsonify(sensors.get_sensorIDs(site)), 200

@app.route("/data/values/site/<measurement>/<site>", methods=['GET',])
def get_meas_site_data(measurement, site):
    '''
    Get a site data keys with a specified measurement
    '''
    return jsonify(sensors.get_sensorIDs(site, measurement)), 200


@app.route("/data/values/type/<Type>", methods=['GET',])

def get_type_data(Type):
    '''
    Get a sensor type data keys
    '''
    content = request.get_json(silent=False)
    return jsonify(sensors.get_type_sensors(Type)), 200

@app.route("/data/values/all", methods=['GET',])
def get_all_sens():
    '''
    Get a sensor type data keys
    '''
    content = request.get_json(silent=False)
    return jsonify(sensors.get_all_sensors()), 200

if __name__ == "__main__":
    app.run()
