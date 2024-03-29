from flask import Flask, request, jsonify
#import creds
import json
import sensor_data as sensors
from init import app

# Sensor data routes ####################################
@app.route("/marcus", methods=['POST',])
def update_data():
    '''
    Writes data to influx from remote sensor
    '''
    print("SEnsor data incoming")
    # print (request.headers)
    print (request.data)
    # content = request.get_json(silent=False)
    content = request.data
    # print (type(content))
    a = content.decode("utf-8", errors='replace')
    print(a)
    # data = json.loads(content.decode("utf-8", errors='replace'))
    b = json.loads(a)
    # stripped = content.encode("ascii", "ignore")
    # print (content)
    print (b)
    # formatted = json.loads(stripped)
    # print (type(stripped))
    # print(stripped)
    # if 'PY' in content and len(content) < 100:
    #try:
    return jsonify(sensors.sort_tank_data(b)), 200
    #except:
    #    return ("Malformed data"), 412
    # else:
    #     return 412

if __name__ == "__main__":
    app.run()
