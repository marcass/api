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
retention_policies = ['24_hours', '7_days','2_months', '1_year', '5_years']
# setup retention policy detail
durations = {'24_hours': {'dur':'1d', 'default':True},
             '7_days': {'dur':'7d', 'default':False},
             '2_months': {'dur':'4w', 'default':False},
             '1_year': {'dur':'52w','default':False},
             '5_years': {'dur':'260w','default':False}}
# orgainse graphing periods
periods = {'hours': ['24_hours'], 'days': ['7_days', '2_months'], 'months': ['1_year'], 'years': ['5_years']}
# def setup_RP():
def setup_RP(meas):
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
        if i in RP_list:
            print 'RP already here'
        else:
            print 'making rp for '+i
            client.create_retention_policy(i, durations[i]['dur'], 1, database='sensors', default=durations[i]['default'])
    # https://influxdb-python.readthedocs.io/en/latest/api-documentation.html
    # https://docs.influxdata.com/influxdb/v1.6/guides/downsampling_and_retention/
    try:
        # client.query('CREATE CONTINUOUS QUERY \"%s\" ON %s BEGIN SELECT mean(temp) AS "temp", mean(humidity) AS "humidity", mean(light) AS "light" INTO \"%s\".values_7d FROM \"%s\" GROUP BY time(5m), * END' %(meas+'_cq_7_days', db_name, meas+'_7_days', meas))
        # client.query('CREATE CONTINUOUS QUERY \"%s\" ON %s BEGIN SELECT mean(temp) AS "temp", mean(humidity) AS "humidity", mean(light) AS "light" INTO \"%s\".values_2mo FROM \"%s\" GROUP BY time(10m), * END' %(meas+'_cq_2_months', db_name, meas+'_2_months', meas))
        # client.query('CREATE CONTINUOUS QUERY \"%s\" ON %s BEGIN SELECT mean(temp) AS "temp", mean(humidity) AS "humidity", mean(light) AS "light" INTO \"%s\".values_1y FROM \"%s\" GROUP BY time(20m), * END' %(meas+'_cq_1_year', db_name, meas+'_1_year', meas))
        # client.query('CREATE CONTINUOUS QUERY \"%s\" ON %s BEGIN SELECT mean(temp) AS "temp", mean(humidity) AS "humidity", mean(light) AS "light" INTO \"%s\".values_5y FROM \"%s\" GROUP BY time(30m), * END' %(meas+'_cq_5_years', db_name, meas+'_5_years', meas))
        # client.query('CREATE CONTINUOUS QUERY \"%s\" ON %s BEGIN SELECT mean(%s) AS \"%s\" INTO "7_days".%s FROM "24_hours".\"%s\" GROUP BY time(5m), * END' %(meas+'_cq_7_days', db_name, meas, meas, meas, meas))
        # client.query('CREATE CONTINUOUS QUERY \"%s\" ON %s BEGIN SELECT mean(%s) AS \"%s\" INTO "2_months".%s FROM "24_hours".\"%s\" GROUP BY time(10m), * END' %(meas+'_cq_2_months', db_name, meas, meas, meas, meas))
        # client.query('CREATE CONTINUOUS QUERY \"%s\" ON %s BEGIN SELECT mean(%s) AS \"%s\" INTO "1_year".%s FROM "24_hours".\"%s\" GROUP BY time(20m), * END' %(meas+'_cq_1_year', db_name, meas, meas, meas, meas))
        # client.query('CREATE CONTINUOUS QUERY \"%s\" ON %s BEGIN SELECT mean(%s) AS \"%s\" INTO "5_years".%s FROM "24_hours".\"%s\" GROUP BY time(30m), * END' %(meas+'_cq_5_years', db_name, meas, meas, meas, meas))
        # print 'making cqs for '+meas
        client.query('CREATE CONTINUOUS QUERY \"%s\" ON %s BEGIN SELECT mean(%s) AS \"%s\" INTO "7_days"."things" FROM "24_hours"."things" GROUP BY time(5m), * END' %(meas+'_cq_7_days', db_name,  meas, meas))
        client.query('CREATE CONTINUOUS QUERY \"%s\" ON %s BEGIN SELECT mean(%s) AS \"%s\" INTO "2_months"."things" FROM "24_hours"."things" GROUP BY time(10m), * END' %(meas+'_cq_2_months', db_name,  meas, meas))
        client.query('CREATE CONTINUOUS QUERY \"%s\" ON %s BEGIN SELECT mean(%s) AS \"%s\" INTO "1_year"."things" FROM "24_hours"."things" GROUP BY time(20m), * END' %(meas+'_cq_1_year', db_name,  meas, meas))
        client.query('CREATE CONTINUOUS QUERY \"%s\" ON %s BEGIN SELECT mean(%s) AS \"%s\" INTO "5_years"."things" FROM "24_hours"."things" GROUP BY time(30m), * END' %(meas+'_cq_5_years', db_name,  meas, meas))
        print 'making cqs for '+meas
    except:
        # already exist
        print "Failed to create CQs, as they already exist"

# setup_RP()

def write_data(json):
    # print json
    # ensure RP's and CQ's in place for new sites
    if json['type'] not in get_data_types():
        setup_RP(json['type'])
    sensType = json['type']
    val = json['value']
    # influx is fropping values if the arrive as truncated floates (eg 16.00 is sent as 16
    # and influx drops point as it won't stuff an int into a float column)
    if (sensType == 'temp') or (sensType == 'humidity'):
        val = float(json['value'])
    try:
        # boiler data
        json_data = [
            {
                'measurement': 'things',
                'tags': {
                    'sensorID': json['sensor'],
                    'site': json['group'],
                    'type': json['type'],
                    'state': json['state']
                },
                'fields': {
                    json['type']: val
                },
                'time': datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                }
            ]
    except:
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
                    json['type']: val
                },
                'time': datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                }
            ]
    client.write_points(json_data)
    return {'Status': 'success', 'Message': 'successfully wrote data points'}
    # except:
    #     return {'Status': 'error', 'Messgage': 'failed to write data points'}

def get_data_types():
    # returnrs a list [light, etc]
    results = client.query('SHOW FIELD KEYS ON "sensors" FROM "things"')
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
        print i
        if i not in sensors_list:
            sensors_list.append(i['value'])
    return sensors_list

def get_all_sensors():
    types = get_data_types()
    sites = get_sites()
    sensors_list = []
    for i in sites:
        sensors_list.append({'site': i, 'data': get_sensorIDs(i)})
    return sensors_list

def get_sensorIDs(site):
    # site is a list of sites, this returns sensor id's wiht emasurement in a site
    types = get_data_types()
    # result = []
    # for x in sites:
    # print x
    ret = {'site': site, 'traces': []}
    for i in types:
        out = client.query('SHOW TAG VALUES ON "sensors" WITH KEY = sensorID WHERE "type" = \'%s\' AND "site" = \'%s\'' %(i, site))
        sens_res = out.get_points()
        for c in sens_res:
            if c:
                ret['traces'].append({'type': i, 'sensorID': c['value'], 'site': site})
    # result.append(ret)
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
    # SHOW TAG VALUES on sensors with key= sensorID where "site" = 'marcus'
    meas_types = results.get_points()
    # sites = np.unique[a['value'] for a in meas_types]
    for a in meas_types:
        if a['value'] not in sites:
            sites.append(a['value'])
    # print sites
    return sites

q_dict = {'24_hours': {'rp_val':'sensorData', 'period_type': 'hours'}, '7_days': {'rp_val':'values_7d', 'period_type': 'days'}, '2_months': {'rp_val':'values_2mo', 'period_type': 'days'}, '1_year': {'rp_val':'values_1y', 'period_type': 'months'}, '5_years': {'rp_val':'values_5y', 'period_type': 'years'}}
def custom_data(payload):
    # print payload
    # {'traces':traces, 'range':range, 'period':period, 'site': values.site}
    try:
        arg_dict = {q_dict[payload['range']]['period_type']: payload['period']}
        print arg_dict
        timestamp = (datetime.datetime.utcnow() - datetime.timedelta(**arg_dict)).strftime("%Y-%m-%dT%H:%M:%S.%f000Z")
    except:
        timestamp = (datetime.datetime.utcnow() - datetime.timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S.%f000Z")
    res = []
    # colours = ['red', 'blue', 'green', 'black', 'yellow', 'orange']
    # count = 0
    thousands = False
    hundreds = False
    tens = False
    # parse values to graph:
    # results = client.query('SELECT * FROM \"%s\".%s WHERE time > \'%s\'' %(payload['range'], val_type, timestamp))
    # setup layout of graph
    layout = {'title': 'House data'}
    for i in payload['traces']:
        trace = i.split('+')
        if len(trace) > 2:
            site, val_type, sensor = i.split('+')
        else:
            val_type, sensor = i.split('+')
            site = payload['site']
        # results = client.query('SELECT * FROM \"%s\".%s WHERE time > now() - \'%s\'' %(payload['range'], val_type, timestamp))
        results = client.query('SELECT * FROM \"%s\"."things" WHERE time > now() - \'%s\' AND "type" = \'%s\' AND "sensorID" = \'%s\' AND "site" = \'%s\'' %(payload['range'], timestamp, val_type, sensor, site))
        # dat = results.get_points(tags={'sensorID':sensor})
        dat = results.get_points()
        times = []
        values = []
        if (val_type == 'light'):
            if not thousands:
                layout.update({'yaxis2': {'title': 'Light', 'overlaying': 'y', 'side': 'right'}})
            thousands = True
            out = {'connectgaps': False, 'name': sensor+' '+val_type, 'type': 'line', 'x': '', 'y': '', 'yaxis': 'y2'}
        if (val_type == 'pid') or (val_type == 'humidity'):
            if not hundreds:
                layout.update({'yaxis3': {'title': 'Percent', 'overlaying': 'y', 'side': 'right', 'anchor': 'free', 'position': 0.85}})
            hundreds = True
            out = {'connectgaps': False, 'name': sensor+' '+val_type, 'type': 'line', 'x': '', 'y': '', 'yaxis': 'y3'}
        if (val_type == 'temp'):
            if not tens:
                layout.update({'yaxis':{'title': 'Temperature'}})
            tens = True
            out = {'connectgaps': False, 'name': sensor+' '+val_type, 'type': 'line', 'x': '', 'y': ''}
        for a in dat:
            times.append(a['time'])
            values.append(a[val_type])
        out['x'] = times
        out['y'] = values
        # out['colour'] = colours[count]
        # count += 1
        res.append(out)
    final_res = {'layout':layout, 'data': res}
    # print final_res
    return {'layout':layout, 'data': res}

def start_data(payload):
    # want to graph sensors from one site, so payload should be in this format:
    # {"site":"marcus", "sensorIDs":[], "range":<RP to graph from>, "period": int}
    # payload = {"measurement": [{"site": <site1>, "sensors":[{'id': <sens1>, 'type': <temp/hum>}........]},....], "range":<RP to graph from>, "period": int}
    # print 'payload for graph is:'
    # print payload
    try:
        arg_dict = {q_dict[payload['range']]['period_type']: payload['period']}
        print arg_dict
        timestamp = (datetime.datetime.utcnow() - datetime.timedelta(**arg_dict)).strftime("%Y-%m-%dT%H:%M:%S.%f000Z")
    except:
    # timestamp = (datetime.datetime.utcnow() - datetime.timedelta(hours=int(payload['period']))).strftime("%Y-%m-%dT%H:%M:%S.%f000Z")
        timestamp = (datetime.datetime.utcnow() - datetime.timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%S.%f000Z")
    # results = client.query('SELECT * FROM "boiler"."autogen"."boilerEvents" WHERE time > %s' %("'"+timestamp+"'"))
    # target = payload["range"]+"."+q_dict[payload["range"]]["rp_val"]
    # print target
    res = []
    # colours = ['red', 'blue', 'green', 'black', 'yellow', 'orange']
    # count = 0
    # results = client.query('SELECT * FROM "24_hours".marcus WHERE time > \'%s\'' %(timestamp))
    results = client.query('SELECT * FROM "7_days".temp WHERE time > now() - \'%s\'' %(timestamp))
    # results = client.query('SELECT * FROM \"%s\".%s WHERE time > \'%s\'' %(payload['range'], q_dict[payload['range']['rp_val']], timestamp))
    # print results.raw
    for x in payload['measurement']:
        for i in x['sensors']:
            # results = client.query('SELECT %s FROM \"%s\".\"%s\" WHERE time > \'%s\'' %(i['type'], payload["range"], payload['measurement'], timestamp))
            times = []
            values = []
            # if i in temps:
            # out = {'marker': {'color': '', 'size': '10', 'symbol': 104}, 'name': i['id'], 'type': 'line', 'x': '', 'y': '', 'yaxis': 'yaxis'}
            out = {'marker': {'color': 'red', 'size': '10'}, 'name': i['id'], 'type': 'line', 'x': '', 'y': ''}
                # data = results.get_points()
            # if i in pids:
            #     out = {'marker': {'color': '', 'size': '10', 'symbol': 104}, 'name': i, 'type': 'line', 'x': '', 'y': '', 'yaxis': 'yaxis2'}
                # data = results.get_points(tags={'status': 'Heating'})
            data = results.get_points(tags={"sensorID": i['id']})
            # print data
            for a in data:
                times.append(a['time'])
                values.append(a[i['type']])
            # out['colour'] = colours[count]
            # count += 1
            out['x'] = times
            out['y'] = values
            # print times
            # print values
            res.append(out)
    # print res
    return res
