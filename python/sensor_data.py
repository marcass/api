from influxdb import InfluxDBClient
from datetime import timedelta
import datetime
import time

measurement = []

db_name = 'sensors'
# setup db
client = InfluxDBClient(host='localhost', port=8086)
# setup db if it ins't already:
def setup_db():
    print 'checking for db'
    flag = False
    dbs = client.get_list_database()
    print dbs
    for i in client.get_list_database():
        if db_name in i['name']:
            flag = True
        else:
            print 'doing nothing'
    if not flag:
        print 'making db'
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
    # try:
    RP = client.get_list_retention_policies(db_name)
    for i in RP:
        # produce list of existing retention policies
        RP_list.append(i['name'])
    # print RP_list
    # except:
    #     print 'No retention polices here'
    for i in retention_policies:
        in_data = meas+'_'+i
        if in_data in RP_list:
            print 'RP already here'
        else:
            print 'making rp for '+in_data
            client.create_retention_policy(in_data, durations[i]['dur'], 1, database='sensors', default=durations[i]['default'])
    # https://influxdb-python.readthedocs.io/en/latest/api-documentation.html
    # https://docs.influxdata.com/influxdb/v1.6/guides/downsampling_and_retention/
    try:
        client.query('CREATE CONTINUOUS QUERY \"%s\" ON %s BEGIN SELECT mean(%s) AS \"%s\" INTO \"%s\".\"%s\" FROM "24_hours".\"%s\" GROUP BY time(2m), * END' %(vtype+'_cq_7_days', db_name,  vtype, vtype, meas+'_7_days', meas, meas))
        client.query('CREATE CONTINUOUS QUERY \"%s\" ON %s BEGIN SELECT mean(%s) AS \"%s\" INTO \"%s\".\"%s\" FROM "24_hours".\"%s\" GROUP BY time(5m), * END' %(vtype+'_cq_2_months', db_name,  vtype, vtype, meas+'_2_months', meas, meas))
        client.query('CREATE CONTINUOUS QUERY \"%s\" ON %s BEGIN SELECT mean(%s) AS \"%s\" INTO \"%s\".\"%s\" FROM "24_hours".\"%s\" GROUP BY time(10m), * END' %(vtype+'_cq_1_year', db_name,  vtype, vtype, meas+'_1_year', meas, meas))
        client.query('CREATE CONTINUOUS QUERY \"%s\" ON %s BEGIN SELECT mean(%s) AS \"%s\" INTO \"%s\".\"%s\" FROM "24_hours".\"%s\" GROUP BY time(20m), * END' %(vtype+'_cq_forever', db_name,  vtype, vtype, meas+'_forever', meas, meas))
        print 'making cqs for '+vtype
    except:
        # already exist
        print "Failed to create CQs, as they already exist"

def write_data(json):
    # incoming format should be:
    # json = {'measurement': 'tablename', 'tags':{'type':'meastype', 'sensorID':'sensor name', 'site': 'thissite'}, 'value':value}
    # print json
    # ensure RP's and CQ's in place for new sites
    if 'measurement' in json:
        measurement = json['measurement']
    else:
        measurement = 'things'
    if 'tags' in json:
        in_type = json['tags']['type']
    if 'type' in json:
        in_type = json['type']
    if in_type not in get_data_types(measurement):
    # try:
        setup_RP(json['type'], measurement)
    # except:
    #     print 'RP in place for '+json['type']+' '+measurement
    sensType = json['type']
    val = json['value']
    # influx is dropping values if the arrive as truncated floates (eg 16.00 is sent as an int of 16 by arduinoJSON
    # and influx drops point as it won't stuff an int into a float column)
    if (sensType == 'temp') or (sensType == 'humidity'):
        val = float(json['value'])
        if val < -100.0:
            return {'Status': 'Error', 'Message': 'Value of '+str(val)+' out of range'}
    # tank data
    if 'measurement' in json:
        json_data = [
            {
                'measurement': json['measurement'],
                'tags': json['tags'],
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
                    'sensorID': json['sensor'],
                    'site': json['group'],
                    'type': json['type']
                },
                'fields': {
                    in_type: val
                },
                'time': datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                }
            ]
    client.write_points(json_data)
    return {'Status': 'success', 'Message': 'successfully wrote data points'}

def get_data_types(meas=0):
    if not meas:
        meas = 'things'
    # returnrs a list [light, etc]
    results = client.query('SHOW FIELD KEYS ON "sensors" FROM \"%s\"' %(meas))
    types = results.get_points()
    types_list = []
    for i in types:
        if i not in types_list:
            types_list.append(i['fieldKey'])
    return types_list

def get_type_sensors(Type):
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
    print traces_list
    return traces_list

def get_all_sensors():
    sites = get_sites()
    sensors_list = []
    for i in sites:
        # sensors_list.append(get_sensorIDs(i))
        sensors_list = sensors_list + get_sensorIDs(i)
    return sensors_list

def get_sensorIDs(site):
    # site is a list of sites, this returns sensor id's wiht emasurement in a site
    types = get_data_types()
    ret = []
    for i in types:
        out = client.query('SHOW TAG VALUES ON "sensors" WITH KEY = sensorID WHERE "type" = \'%s\' AND "site" = \'%s\'' %(i, site))
        sens_res = out.get_points()
        for c in sens_res:
            if c:
                ret.append({'type': i, 'sensorID': c['value'], 'site': site})
    return ret


def get_measurements():
    results = client.query('SHOW MEASUREMENTS ON "sensors"')
    measurement = results.get_points()
    types = []
    for i in measurement:
        types.append(i['name'])
    return types

def get_sites():
    sites = []
    results = client.query('SHOW TAG VALUES ON "sensors" WITH KEY = site')
    meas_types = results.get_points()
    for a in meas_types:
        if a['value'] not in sites:
            sites.append(a['value'])
    return sites

#q_dict = {'24_hours': {'rp_val':'sensorData', 'period_type': 'hours'}, '7_days': {'rp_val':'values_7d', 'period_type': 'days'}, '2_months': {'rp_val':'values_2mo', 'period_type': 'days'}, '1_year': {'rp_val':'values_1y', 'period_type': 'months'}, 'forever': {'rp_val':'values    _5y', 'period_type': 'years'}}
q_dict = {'24_hours': {'rp_val':'sensorData', 'period_type': 'hours'}, '7_days': {'rp_val':'values_7d', 'period_type': 'days'}, '2_months': {'rp_val':'values_2mo', 'period_type': 'days'}, '1_year': {'rp_val':'values_1y', 'period_type': 'months'}, 'forever': {'rp_val':'values_5y', 'period_type': 'years'}}
def custom_data(payload):
    if 'measurement' in payload:
        ret_pol = payload['measurement']+'_'+payload['range']
    else:
        ret_pol = 'things_'+payload['range']
    # print payload
    # {'traces':traces, 'range':range, 'period':period, 'site': values.site}
    # try:
    arg_dict = {q_dict[payload['range']]['period_type']: int(payload['period'])}
    # print arg_dict
    timestamp = (datetime.datetime.utcnow() - datetime.timedelta(**arg_dict)).strftime("%Y-%m-%dT%H:%M:%S.%f000Z")
    # print timestamp
    # except:
    #     timestamp = (datetime.datetime.utcnow() - datetime.timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S.%f000Z")
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
                print site, val_type, sensor
        except:
            print('fuckup.')
        results = client.query('SELECT * FROM \"%s\"."things" WHERE time > \'%s\' AND time < now() AND "type" = \'%s\' AND "sensorID" = \'%s\' AND "site" = \'%s\'' %(ret_pol, timestamp, val_type, sensor, site))
        #results = client.query('SELECT * FROM \"%s\"."things" WHERE time > now() - \'%s\' AND "type" = \'%s\' AND "sensorID" = \'%s\' AND "site" = \'%s\'' %(payload['range'], timestamp, val_type, sensor, site))
        dat = results.get_points()
        times = []
        values = []
        if (val_type == 'light'):
            if not thousands:
                layout.update({'yaxis2': {'title': 'Light', 'overlaying': 'y', 'side': 'right'}})
            thousands = True
            out = {'connectgaps': False, 'name': site+' '+sensor+' '+val_type, 'type': 'line', 'x': '', 'y': '', 'yaxis': 'y2'}
        if (val_type == 'pid') or (val_type == 'humidity') or ((val_type == 'temp') and (site == 'boiler')):
            if not hundreds:
                layout.update({'yaxis3': {'title': 'Percent', 'overlaying': 'y', 'side': 'right', 'anchor': 'free', 'position': 0.85}})
            hundreds = True
            out = {'connectgaps': False, 'name': site+' '+sensor+' '+val_type, 'type': 'line', 'x': '', 'y': '', 'yaxis': 'y3'}
        if (val_type == 'temp') and (site != 'boiler'):
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
    try:
        arg_dict = {q_dict[payload['range']]['period_type']: payload['period']}
        print arg_dict
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
# {u'range': u'7_days', u'traces': [{u'members': [{u'sensorID': u'dining', u'type': u'temp', u'site': u'julian'}, {u'sensorID': u'upstairs', u'type': u'temp', u'site': u'julian'}], u'yaxis': u'y'}, {u'members': [{u'sensorID': u'heater', u'type': u'temp', u'site': u'julian'}], u'yaxis': u'y2'}, {u'members': [], u'yaxis': u'y3'}], u'period': 1, u'site': u'julian'}
# {u'members': [{u'sensorID': u'dining', u'type': u'temp', u'site': u'julian'}, {u'sensorID': u'upstairs', u'type': u'temp', u'site': u'julian'}], u'yaxis': u'y'}
    arg_dict = {q_dict[payload['range']]['period_type']: int(payload['period'])}
    timestamp = (datetime.datetime.utcnow() - datetime.timedelta(**arg_dict)).strftime("%Y-%m-%dT%H:%M:%S.%f000Z")
    res = []
    # setup layout of graph
    layout = {'title': 'House data'}
    site = payload['site']
    if 'measurement' in payload:
        ret_pol = payload['measurement']+'_'+payload['range']
    else:
        ret_pol = 'things_'+payload['range']
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
            results = client.query('SELECT * FROM \"%s\"."things" WHERE time > \'%s\' AND time < now() AND "type" = \'%s\' AND "sensorID" = \'%s\' AND "site" = \'%s\'' %(ret_pol, timestamp, val_type, sensor, site))
            #results = client.query('SELECT * FROM \"%s\"."things" WHERE time > now() - \'%s\' AND "type" = \'%s\' AND "sensorID" = \'%s\' AND "site" = \'%s\'' %(payload['range'], timestamp, val_type, sensor, site))
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
