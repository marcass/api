# from influxdb import InfluxDBClient
# from datetime import timedelta
# import datetime
# import time
import re
import json

measurement = []

# sanitise strings to reduce sql-injection issues
def clean(data):
    if isinstance(data, str) or isinstance(data, unicode):
        return re.sub('[^A-Za-z0-9\-_]+', '', data)
    if isinstance(data, dict):
        data = json.dumps(data)
        data = re.sub('[^A-Za-z0-9\-_{}:\',+\."\[\]]+', '', data)
        return json.loads(data)

def clean_debug(data):
    print 'data in = '+str(data)
    print 'type of data is '+str(type(data))
    if isinstance(data, str) or isinstance(data, unicode):
        print 'dirty string = '+data
        data = re.sub('[^A-Za-z0-9\-_]+', '', data)
        print 'cleaned string = '+data
        return re.sub('[^A-Za-z0-9\-_]+', '', data)
    if isinstance(data, dict):
        print 'dirty dict = '+str(data)
        data = json.dumps(data)
        print 'dirty dict as a string = '+data
        data = re.sub('[^A-Za-z0-9\-_{}:\',+\."\[\]]+', '', data)
        print 'cleaned dict string = '+data
        return json.loads(data)



def write_data(data):
    # data = clean(data)
    print data
    print type(data)
    data_dict = json.loads(data)
    print type(data)
    # if 'measurement' in data:
    #     json_data = [
    #         {
    #             'measurement': data['measurement'],
    #             'tags': data['tags'],
    #             'fields': {
    #                 in_type: val
    #             },
    #             'time': datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    #             }
    #         ]
    # else:
    #     # default measuremtn for esp sensors
    #     measurement = 'things'
    #     json_data = [
    #         {
    #             'measurement': measurement,
    #             'tags': {
    #                 'sensorID': data['sensor'],
    #                 'site': data['group'],
    #                 'type': data['type']
    #             },
    #             'fields': {
    #                 in_type: val
    #             },
    #             'time': datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    #             }
    #         ]
    # try:
    #     client.write_points(json_data)
    #     return {'Status': 'success', 'Message': 'successfully wrote data points'}
    # except:
    #     return {'Status': 'failed', 'Message': 'exception'}
