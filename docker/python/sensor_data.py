from influxdb import InfluxDBClient
from datetime import timedelta
import datetime
import time
import re
import json

measurement = []

db_name = 'sensors'
# setup db
# host is in docker network called 'vexme' so can be found by ddocker hostname (influxdb)
client = InfluxDBClient(host='localhost', port=8086)
# setup db if it ins't already:
def setup_db():
    print('checking for db')
    flag = False
    dbs = client.get_list_database()
    print(dbs)
    for i in client.get_list_database():
        if db_name in i['name']:
            flag = True
        else:
            print('doing nothing')
    if not flag:
        print('making db')
        client.create_database(db_name)

# setup db and use currnet db
setup_db()
client.switch_database(db_name)
# client.drop_database(db_name)

# setup reteniton plicy list must match index of durations
retention_policies = ['24_hours', '7_days','2_months', '1_year', 'forever']
# setup retention policy detail
durations = {'24_hours': {'dur':'1d', 'default':True},
             '7_days': {'dur':'7d', 'default':False},
             '2_months': {'dur':'4w', 'default':False},
             '1_year': {'dur':'52w','default':False},
             'forever': {'dur':'INF','default':False}}
# orgainse graphing periods
periods = {'hours': ['24_hours'], 'days': ['7_days', '2_months'], 'months': ['1_year'], 'years': ['forever']}
def setup_RP(vtype, meas):
    global retention_policies
    global measurement
    RP_list = []
    try:
        RP = client.get_list_retention_policies(db_name)
        for i in RP:
            # produce list of existing retention policies
            RP_list.append(i['name'])
            #print (RP_list)
    except:
        print ('No retention polices here')
    for i in retention_policies:
        if i in RP_list:
            #print('RP already here')
        else:
            print('making rp for '+i)
            client.create_retention_policy(i, durations[i]['dur'], 1, database=db_name, default=durations[i]['default'])
    # https://influxdb-python.readthedocs.io/en/latest/api-documentation.html
    # https://docs.influxdata.com/influxdb/v1.6/guides/downsampling_and_retention/
    try:
        client.query('CREATE CONTINUOUS QUERY \"%s\" ON %s BEGIN SELECT mean(%s) AS \"%s\" INTO "7_days".\"%s\" FROM "24_hours".\"%s\" GROUP BY time(2m), * END' %(vtype+'_cq_7_days', db_name,  vtype, vtype, meas, meas))
        client.query('CREATE CONTINUOUS QUERY \"%s\" ON %s BEGIN SELECT mean(%s) AS \"%s\" INTO "2_months".\"%s\" FROM "24_hours".\"%s\" GROUP BY time(5m), * END' %(vtype+'_cq_2_months', db_name,  vtype, vtype, meas, meas))
        client.query('CREATE CONTINUOUS QUERY \"%s\" ON %s BEGIN SELECT mean(%s) AS \"%s\" INTO "1_year".\"%s\" FROM "24_hours".\"%s\" GROUP BY time(10m), * END' %(vtype+'_cq_1_year', db_name,  vtype, vtype, meas, meas))
        client.query('CREATE CONTINUOUS QUERY \"%s\" ON %s BEGIN SELECT mean(%s) AS \"%s\" INTO "forever".\"%s\" FROM "24_hours".\"%s\" GROUP BY time(20m), * END' %(vtype+'_cq_forever', db_name,  vtype, vtype, meas, meas))
        print('making cqs for '+vtype)
    except:
        # already exist
        print("Failed to create CQs, as they already exist")

# sanitise strings to reduce sql-injection issues
def clean(data):
    if isinstance(data, str) or isinstance(data, str):
        return re.sub('[^A-Za-z0-9\-_]+', '', data)
    if isinstance(data, dict):
        data = json.dumps(data)
        data = re.sub('[^A-Za-z0-9\-_{}:\',+\."\[\]]+', '', data)
        return json.loads(data)

def clean_debug(data):
    print('data in = '+str(data))
    print('type of data is '+str(type(data)))
    if isinstance(data, str) or isinstance(data, str):
        print('dirty string = '+data)
        data = re.sub('[^A-Za-z0-9\-_]+', '', data)
        print('cleaned string = '+data)
        return re.sub('[^A-Za-z0-9\-_]+', '', data)
    if isinstance(data, dict):
        print('dirty dict = '+str(data))
        data = json.dumps(data)
        print('dirty dict as a string = '+data)
        data = re.sub('[^A-Za-z0-9\-_{}:\',+\."\[\]]+', '', data)
        print('cleaned dict string = '+data)
        return json.loads(data)



def write_data(data):
    data = clean(data)
    # incoming format should be:
    # data = {'measurement': 'tablename', 'tags':{'type':'meastype', 'sensorID':'sensor name', 'site': 'thissite'}, 'value':value}
    #print (data)
    # ensure RP's and CQ's in place for new sites
    if 'measurement' in data:
        measurement = data['measurement']
    else:
        measurement = 'things'
    if 'tags' in data:
        in_type = data['tags']['type']
    if 'type' in data:
        in_type = data['type']
    if in_type not in get_data_types(measurement):
        try:
            setup_RP(in_type, measurement)
        except:
            print('RP in place for '+data['type']+' '+measurement)
    val = data['value']
    # influx is dropping values if the arrive as truncated floates (eg 16.00 is sent as an int of 16 by arduinoJSON
    # and influx drops point as it won't stuff an int into a float column)
    if (in_type == 'temp') or (in_type == 'humidity'):
        val = float(data['value'])
        if val < -100.0:
            return {'Status': 'Error', 'Message': 'Value of '+str(val)+' out of range'}
    # tank data
    if 'measurement' in data:
        json_data = [
            {
                'measurement': data['measurement'],
                'tags': data['tags'],
                'fields': {
                    in_type: val
                },
                'time': datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                }
            ]
    else:
        # default measuremtn for esp sensors
        measurement = 'things'
        json_data = [
            {
                'measurement': measurement,
                'tags': {
                    'sensorID': data['sensor'],
                    'site': data['group'],
                    'type': data['type']
                },
                'fields': {
                    in_type: val
                },
                'time': datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                }
            ]
    try:
        client.write_points(json_data)
        return {'Status': 'success', 'Message': 'successfully wrote data points'}
    except:
        return {'Status': 'failed', 'Message': 'exception'}

def get_data_types(meas=0):
    # returnrs a list [light, etc]
    if meas == 0:
        results = client.query('SHOW FIELD KEYS ON "sensors"')
    else:
        meas = clean(meas)
        results = client.query('SHOW FIELD KEYS ON "sensors" FROM \"%s\"' %(meas))
    types = results.get_points()
    types_list = []
    for i in types:
        if i not in types_list:
            types_list.append(i['fieldKey'])
    return types_list

def get_type_sensors(Type):
    Type = clean(Type)
    # returns all sensots that maesure than type (eg light)
    results = client.query('SHOW TAG VALUES ON "sensors" WITH KEY = sensorID WHERE "type" = \'%s\'' %(Type))
    out = results.get_points()
    sensors_list = []
    for i in out:
        if i not in sensors_list:
            sensors_list.append(i['value'])
    traces_list = []
    for x in sensors_list:
        results = client.query('SHOW TAG VALUES ON "sensors" WITH KEY = site WHERE "sensorID" = \'%s\'' %(x))
        out = results.get_points()
        for c in out:
            traces_list.append({'site': c['value'], 'sensorID':x})
    # print traces_list
    return traces_list

def get_all_sensors():
    sites = get_sites()
    sensors_list = []
    for i in sites:
        # sensors_list.append(get_sensorIDs(i))
        sensors_list = sensors_list + get_sensorIDs(i)
    return sensors_list

def get_sensorIDs(site, meas=0):
    site = clean(site)
    if meas == 0:
        types = []
        for i in get_measurements():
            types.append(get_data_types(i))
    else:
        meas = clean(meas)
        types = get_data_types(meas)
    ret = []
    for i in types:
        try:
            out = client.query('SHOW TAG VALUES ON "sensors" WITH KEY = sensorID WHERE "type" = \'%s\' AND "site" = \'%s\'' %(i, site))
            sens_res = out.get_points()
            for c in sens_res:
                if c:
                    ret.append({'type': i, 'sensorID': c['value'], 'site': site})
        except:
            print('Just foolin, none of that combo here')
    return ret


def get_measurements():
    results = client.query('SHOW MEASUREMENTS ON "sensors"')
    measurement = results.get_points()
    meas = []
    for i in measurement:
        meas.append(i['name'])
    return meas

def get_sites():
    sites = []
    measurements = []
    ret_sites = []
    results = client.query('SHOW TAG VALUES ON "sensors" WITH KEY = site')
    meas_types = results.get_points()
    # print meas_types
    for a in meas_types:
        # print a
        # res = {'sitename': '', 'measurement': ''}
        if a['value'] not in sites:
            # print a['value']
            sites.append(a['value'])
            # res['sitename'] = a['value']
            get_meas = client.query('SHOW MEASUREMENTS ON "sensors" WHERE "site" = \'%s\'' %(a['value']))
            meas_out = get_meas.get_points()
            for i in meas_out:
                # if res['measurement'] == '':
                measurements.append(i['name'])
                    # res['measurement'] = i['name']
            # ret_sites.append(res)
            #     print a
    # print ret_sites
    # print [sites, measurements]
    return [sites, measurements]

q_dict = {'24_hours': {'period_type': 'hours', 'mulitplier': 1},
          '7_days': {'period_type': 'days', 'mulitplier': 1},
          '2_months': {'period_type': 'days', 'mulitplier': 1},
          '1_year': {'period_type': 'days', 'mulitplier': 30},
          'forever': {'period_type': 'weeks', 'mulitplier': 52}}
def custom_data(payload):
    payload = clean(payload)
    ret_pol = payload['range']
    arg_dict = {q_dict[payload['range']]['period_type']: (int(payload['period'])*q_dict[payload['range']]['mulitplier'])}
    timestamp = (datetime.datetime.utcnow() - datetime.timedelta(**arg_dict)).strftime("%Y-%m-%dT%H:%M:%S.%f000Z")
    res = []
    # setup layout of graph
    thousands = False
    hundreds = False
    tens = False
    layout = {'title': 'House data'}
    for i in payload['traces']:
        try:
            if 'type' in payload:
                val_type = payload['type']
                site, sensor = i.split('+')
            elif 'site' in payload:
                site = payload['site']
                val_type, sensor = i.split('+')
            else:
                site, val_type, sensor = i.split('+')
                print(site, val_type, sensor)
        except:
            print('fuckup.')
        if 'measurement' in payload:
            meas = payload['measurement']
            if meas == '':
                meas = 'things'
        else:
            meas = 'things'
        results = client.query('SELECT * FROM \"%s\".\"%s\" WHERE time > \'%s\' AND time < now() AND "type" = \'%s\' AND "sensorID" = \'%s\' AND "site" = \'%s\'' %(ret_pol, meas, timestamp, val_type, sensor, site))
        dat = results.get_points()
        times = []
        values = []
        if (val_type == 'light'):
            if not thousands:
                layout.update({'yaxis2': {'title': 'Light', 'overlaying': 'y', 'side': 'right'}})
            thousands = True
            out = {'connectgaps': False, 'name': site+' '+sensor+' '+val_type, 'type': 'line', 'x': '', 'y': '', 'yaxis': 'y2'}
        if (val_type == 'pid') or (val_type == 'humidity') or (val_type == 'water_level') or ((val_type == 'temp') and (site == 'boiler')):
            if not hundreds:
                layout.update({'yaxis3': {'title': 'Percent', 'overlaying': 'y', 'side': 'right', 'anchor': 'free', 'position': 0.85}})
            hundreds = True
            out = {'connectgaps': False, 'name': site+' '+sensor+' '+val_type, 'type': 'line', 'x': '', 'y': '', 'yaxis': 'y3'}
        if ((val_type == 'temp') and (site != 'boiler')) or (val_type == 'batt_level'):
            if not tens:
                layout.update({'yaxis':{'title': 'Temperature'}})
            tens = True
            out = {'connectgaps': False, 'name': site+' '+sensor+' '+val_type, 'type': 'line', 'x': '', 'y': ''}
        for a in dat:
            times.append(a['time'])
            values.append(a[val_type])
        out['x'] = times
        out['y'] = values
        res.append(out)
    final_res = {'layout':layout, 'data': res}
    return {'layout':layout, 'data': res}

def start_data(payload):
    payload = clean(payload)
    try:
        arg_dict = {q_dict[payload['range']]['period_type']: payload['period']}
        timestamp = (datetime.datetime.utcnow() - datetime.timedelta(**arg_dict)).strftime("%Y-%m-%dT%H:%M:%S.%f000Z")
    except:
        timestamp = (datetime.datetime.utcnow() - datetime.timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%S.%f000Z")
    res = []
    results = client.query('SELECT * FROM "7_days".temp WHERE time > now() - \'%s\'' %(timestamp))
    for x in payload['measurement']:
        for i in x['sensors']:
            times = []
            values = []
            out = {'marker': {'color': 'red', 'size': '10'}, 'name': i['id'], 'type': 'line', 'x': '', 'y': ''}
            data = results.get_points(tags={"sensorID": i['id']})
            for a in data:
                times.append(a['time'])
                values.append(a[i['type']])
            out['x'] = times
            out['y'] = values
            res.append(out)
    return res

def custom_ax(payload):
    payload = clean(payload)
# {u'range': u'7_days', u'traces': [{u'members': [{u'sensorID': u'dining', u'type': u'temp', u'site': u'julian'}, {u'sensorID': u'upstairs', u'type': u'temp', u'site': u'julian'}], u'yaxis': u'y'}, {u'members': [{u'sensorID': u'heater', u'type': u'temp', u'site': u'julian'}], u'yaxis': u'y2'}, {u'members': [], u'yaxis': u'y3'}], u'period': 1, u'site': u'julian'}
# {u'members': [{u'sensorID': u'dining', u'type': u'temp', u'site': u'julian'}, {u'sensorID': u'upstairs', u'type': u'temp', u'site': u'julian'}], u'yaxis': u'y'}
    arg_dict = {q_dict[payload['range']]['period_type']: int(payload['period'])}
    timestamp = (datetime.datetime.utcnow() - datetime.timedelta(**arg_dict)).strftime("%Y-%m-%dT%H:%M:%S.%f000Z")
    res = []
    # setup layout of graph
    layout = {'title': 'House data'}
    site = payload['site']
    ret_pol = payload['range']
    for a in payload['traces']:
        title = a['label']
        if a['yaxis'] == 'y':
            if title != '':
                layout.update({'yaxis': {'title': title}})
            else:
                layout.update({'yaxis': {'title': 'y1'}})
        else:
            if a['yaxis'] == 'y2':
                if title != '':
                    layout.update({'yaxis2': {'title': title, 'overlaying': 'y', 'side': 'right'}})
                else:
                    layout.update({'yaxis2': {'title': 'y2', 'overlaying': 'y', 'side': 'right'}})
            if a['yaxis'] == 'y3':
                if title != '':
                    layout.update({'yaxis3': {'title': title, 'overlaying': 'y', 'side': 'right', 'anchor': 'free', 'position': 0.85}})
                else:
                    layout.update({'yaxis3': {'title': 'y3', 'overlaying': 'y', 'side': 'right', 'anchor': 'free', 'position': 0.85}})
        axis = a['yaxis']
        for i in a['members']:
            try:
                sensor = i['sensorID']
                val_type = i['type']
            except:
                print('fuckup.')
            if 'measurement' in payload:
                meas = payload['measurement']
            else:
                meas = 'things'
            results = client.query('SELECT * FROM \"%s\".\"%s\" WHERE time > \'%s\' AND time < now() AND "type" = \'%s\' AND "sensorID" = \'%s\' AND "site" = \'%s\'' %(ret_pol, meas, timestamp, val_type, sensor, site))
            dat = results.get_points()
            times = []
            values = []
            out = {'connectgaps': False, 'name': site+' '+sensor+' '+val_type, 'type': 'line', 'x': '', 'y': '', 'yaxis': axis}
            for a in dat:
                times.append(a['time'])
                values.append(a[val_type])
            out['x'] = times
            out['y'] = values
            res.append(out)
    final_res = {'layout':layout, 'data': res}
    return {'layout':layout, 'data': res}
