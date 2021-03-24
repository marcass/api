import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import creds
import ast
import requests


# {"timestamp":1549074071149,"name":"5A00080205816410","signature":"T5A00080205816410","signal":22.25}
# {"timestamp":1549074072304,"name":"60000003AEF86C28","signature":"T60000003AEF86C28","signal":20.9375}
# {"timestamp":1549074073250,"name":"9A000003AEE20728","signature":"T9A000003AEE20728","signal":24.3125}
# {"timestamp":1549074074328,"name":"DE0008018486AF10","signature":"TDE0008018486AF10","signal":23.4375}
# {"timestamp":1549074067500,"name":"01000801848CC710","signature":"T01000801848CC710","signal":22.3125}
# {"timestamp":1549074068704,"name":"01000802055D6B10","signature":"T01000802055D6B10","signal":24.875}
# {"timestamp":1549074069936,"name":"110008020565B910","signature":"T110008020565B910","signal":23.75}
# {"timestamp":1549074075548,"name":"01000801848CC710","signature":"T01000801848CC710","signal":22.3125}
# {"timestamp":1549074076755,"name":"01000802055D6B10","signature":"T01000802055D6B10","signal":24.875}
# {"timestamp":1549074077979,"name":"110008020565B910","signature":"T110008020565B910","signal":23.75}

# {"timestamp":1616473399054,"name":"lounge","signature":"c904c1be49128f48ec7","mode":"Heating","state":"OFF","thermostatSignal":0.0,"currentTemperature":21.875,"setpointTemperature":10.0,"enabled":false,"onHold":false,"voting":true,"deviation.setpoint":0.0,"deviation.enabled":false,"deviation.voting":false}
# {"timestamp":1616473400228,"name":"bed_kids","signature":"8b77fd361687f07faa4","mode":"Heating","state":"OFF","thermostatSignal":0.0,"currentTemperature":19.8125,"setpointTemperature":10.0,"enabled":false,"onHold":false,"voting":true,"deviation.setpoint":0.0,"deviation.enabled":false,"deviation.voting":false}
# {"timestamp":1616473401383,"name":"spare_room","signature":"7fbe653d161f6e596d4","mode":"Heating","state":"OFF","thermostatSignal":0.0,"currentTemperature":20.75,"setpointTemperature":10.0,"enabled":false,"onHold":false,"voting":true,"deviation.setpoint":0.0,"deviation.enabled":false,"deviation.voting":false}
# {"timestamp":1616473402538,"name":"bed_master","signature":"ccfb820c067901cc375","mode":"Heating","state":"OFF","thermostatSignal":0.0,"currentTemperature":21.375,"setpointTemperature":10.0,"enabled":false,"onHold":false,"voting":true,"deviation.setpoint":0.0,"deviation.enabled":false,"deviation.voting":false}
# {"timestamp":1616473403726,"name":"hall","signature":"5ab06702d8b598415f7","mode":"Heating","state":"OFF","thermostatSignal":0.0,"currentTemperature":20.5,"setpointTemperature":10.0,"enabled":false,"onHold":false,"voting":true,"deviation.setpoint":0.0,"deviation.enabled":false,"deviation.voting":false}
# {"timestamp":1616473396809,"name":"downstairs","signature":"e056ec84dfbbe69b5ec","mode":"Heating","state":"OFF","thermostatSignal":0.0,"currentTemperature":19.6875,"setpointTemperature":10.0,"enabled":false,"onHold":false,"voting":true,"deviation.setpoint":0.0,"deviation.enabled":false,"deviation.voting":false}

sensor_names = {'5A00080205816410':'hall', '60000003AEF86C28': 'downstairs', '9A000003AEE20728': 'outside',
                'DE0008018486AF10': 'lounge', '01000801848CC710': 'harris', '01000802055D6B10': 'spare',
                '110008020565B910': 'marcus'}

# data = {'measurement': 'tablename', 'tags':{'type':'meastype', 'sensorID':'sensor name', 'site': 'thissite'}, 'value':value}

broker = creds.broker
auth = creds.mosq_auth
AUTH_URL = 'https://skibo.duckdns.org/api/auth/login'
DATA_URL = 'https://skibo.duckdns.org/api/data'
headers = ''
jwt = ''

def getToken():
    global jwt
    global headers
    r = requests.post(AUTH_URL, json = {'username': creds.user, 'password': creds.password})
    tokens = r.json()
    print ('token data is: ' +str(tokens))
    try:
        jwt = tokens['access_token']
        headers = {"Authorization":"Bearer %s" %jwt}
        #print('got token')
    except:
        print('oops, no token for you')

def post_data(data):
    global jwt
    global headers
    if (jwt == ''):
        print('Getting token')
        getToken()
    ret = requests.post(DATA_URL, json = data, headers = headers)
    #print ('JWT = '+str(jwt))
    #print ('First response is: ' +str(ret))
    #if '200' in str(ret):
        #print('Data posted')
        #print(data)
    if '200' not in str(ret):
        print('Oops, not authenticated')
        try:
            getToken()
            requests.post(DATA_URL, json = data, headers = headers)
            ret = {'Status': 'Error', 'Message': 'Got token'}
            print('Post NOT 200 response is: ' +str(r))
        except:
            ret =  {'Status': 'Error', 'Message': 'Failed ot get token, so cannot perform request'}


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("hcc/#", 2)

# use to auth through endpoint
def on_message(client, userdata, msg):
    try:
        message = ast.literal_eval(msg.payload.decode('UTF-8'))
    except:
        print('Could not decode message')
    if 'boiler' in msg.topic:
        try:
            #print('Posting boiler data')
            post_data(message)
        except:
            print('Problem with posting message from boiler')
            pass
    else:
        try:
            sensor = message['name']
            temp = float(message['currentTemperature'])
            data = {'measurement': 'things', 'tags':{'type':'temp', 'sensorID':sensor, 'site': 'marcus'}, 'value':temp}
            post_data(data)
            try:
                if message['state'] = "ON":
                    data = {'measurement': 'things', 'tags':{'type':'state', 'sensorID':sensor, 'site': 'marcus'}, 'value':message['state']}
                    post_data(data)
            except:
                print('Unable to parse state info from thermostat')
                pass
        # try:
        #     sensor = sensor_names[message['name']]
        #     temp = float(message['signal'])
        #     data = {'measurement': 'things', 'tags':{'type':'temp',
        #             'sensorID':sensor, 'site': 'marcus'}, 'value':temp}
        #     post_data(data)
        except:
            print('unable to format message for posting')


#subscribe to broker and test for messages below alert values
client = mqtt.Client("Python_temps")
# not using auth wiht hcc data
# client.username_pw_set(username=auth['username'], password=auth['password'])
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker, 1883, 60)
#client.loop_start()
client.loop_forever()
