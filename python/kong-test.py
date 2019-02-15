from flask import Flask, request, jsonify
import json
from init import app

@app.route("/data", methods=['POST',])
def update_data():
    '''
    Post test
    '''
    print ("headers are:"")
    print (request.headers)
    content = request.get_json(silent=False)
    print (content)
    return jsonify(content), 200

@app.route("/hello", methods=['GET',])
def update_data():
    '''
    Get test
    '''
    print ("headers are:"")
    print (request.headers)
    content = request.get_json(silent=False)
    print (content)
    print("Hello thre konga")
    return jsonify(content), 200


# @app.route("/data", methods=['GET',])
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
#
#
# @app.route("/data/values", methods=['POST',])
# def get_values():
#     '''
#     Get data from influx
#     sends: {"measurement": [{"location": <location1>, "sensors":[{'id': <sens1>, 'type': <temp/hum>}........]},....], "range":<RP to graph from>, "period": int}
#     returns: traces for plotly
#     '''
#     content = request.get_json(silent=False)
#     # print 'views content is:'
#     # print content
#     return jsonify(sensors.start_data(content)), 200
#
#
# @app.route("/data/values/custom", methods=['POST',])
# def get_cust_values():
#     '''
#     Get data from influx
#     sends: {"measurement": [{"location": <location1>, "sensors":[{'id': <sens1>, 'type': <temp/hum>}........]},....], "range":<RP to graph from>, "period": int}
#     returns: traces for plotly
#     '''
#     content = request.get_json(silent=False)
#     # print 'views content is:'
#     # print content
#     return jsonify(sensors.custom_data(content)), 200
#
# @app.route("/data/values/customAx", methods=['POST',])
# def get_cust_axes():
#     '''
#     Get data from influx
#     sends: {"site": site, "traces": [{"senosorID": "lounge", "site": "julian", "type": "light"}, .....], "range":<RP to graph from>, "period": int}
#     returns: traces for plotly
#     '''
#     content = request.get_json(silent=False)
#     # print 'views content is:'
#     # print content
#     return jsonify(sensors.custom_ax(content)), 200
#
# @app.route("/data/values/sites", methods=['GET',])
# def get_sites():
#     '''
#     Get a list of sites
#     '''
#     sites = sensors.get_sites()
#     # Need some way for kong to spit out user here, or change routes dynamically
#     if user_data['role'] == 'admin':
#         ret = []
#         for i in sites[0]:
#             loc = sites[0].index(i)
#             ret.append({'sitename':sites[0][loc], 'measurement': sites[1][loc]})
#         return jsonify(ret), 200
#     # content = request.get_json(silent=False)
#     else:
#         if 'sites' in user_data:
#             allowed_sites = []
#             for i in user_data['sites']:
#                 allowed = json.loads(i)
#                 if allowed['sitename'] in sites[0]:
#                     loc = sites[0].index(allowed['sitename'])
#                     allowed_sites.append({'sitename':sites[0][loc], 'measurement':sites[1][loc]})
#             return jsonify(allowed_sites), 200
#
#
# @app.route("/data/values/types", methods=['GET',])
# def get_types():
#     '''
#     Get a list of types
#     '''
#     return jsonify(sensors.get_data_types()), 200
#
# @app.route("/data/values/site/<site>", methods=['GET',])
# def get_site_data(site):
#     '''
#     Get a site data keys without specifying measurement
#     '''
#     return jsonify(sensors.get_sensorIDs(site)), 200
#
# @app.route("/data/values/site/<measurement>/<site>", methods=['GET',])
# def get_meas_site_data(measurement, site):
#     '''
#     Get a site data keys with a specified measurement
#     '''
#     return jsonify(sensors.get_sensorIDs(site, measurement)), 200
#
#
# @app.route("/data/values/type/<Type>", methods=['GET',])
#
# def get_type_data(Type):
#     '''
#     Get a sensor type data keys
#     '''
#     content = request.get_json(silent=False)
#     return jsonify(sensors.get_type_sensors(Type)), 200
#
# @app.route("/data/values/all", methods=['GET',])
# def get_all_sens():
#     '''
#     Get a sensor type data keys
#     '''
#     content = request.get_json(silent=False)
#     return jsonify(sensors.get_all_sensors()), 200

if __name__ == "__main__":
    app.run()
