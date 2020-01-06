from flask import Flask, request, jsonify
import creds
import json
import sensor_data as sensors
from init import app

# Sensor data routes ####################################
@app.route("/tanks", methods=['POST',])
def update_data():
    '''
    Writes data to influx from remote sensor
    '''
    #print("SEnsor data incoming")
    # print (request.headers)
    content = request.get_json(silent=False)
    # print (content)
    # if 'PY' in content and len(content) < 100:
    return jsonify(sensors.sort_tank_data(content)), 200
    # else:
    #     return 412

if __name__ == "__main__":
    app.run()
