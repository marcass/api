# USAGE:
# INSTALL: sudo pip install flask flask-cors pyopenssl
#
# START REST API WITH ADMIN AUTH:
# python views.py admin pass

# In another terminal:
# curl -X GET http://127.0.0.1:5000/users

# curl -X GET http://127.0.0.1:5000/listallowed

# curl -X GET http://127.0.0.1:5000/door/status

# curl -X POST -H "Content-Type: application/json" -d '{"door":"topgarage", "pincode":"000"}' http://127.0.0.1:5000/usekey
# Response: {"pin_correct": False}

# curl -X POST -H "Content-Type: application/json" -d '{"door":"topgarage", "pincode":"1111"}' http://127.0.0.1:5000/usekey
# Response:  {"pin_correct": True}

# curl -X POST -H "Content-Type: application/json" -d '{"door":"topgarage", "pincode":"1111"}' http://127.0.0.1:5000/usekey
# Response:  {"pin_correct": False} # NOW FALSE because it was a burn code!

# curl -X POST -H "Content-Type: application/json" -d '{"username": "max", "keycode": "AAB23", "doorlist":["topgarage", "frontdoor", "bottomgarage"], "enabled":"1"}' http://127.0.0.1:5000/user
# Response:  {  "Status": "Added key" }

# curl -X POST -H "Content-Type: application/json" -d '{"username": "mw", "keycode": "1111", "doorlist":["topgarage", "frontdoor"], "enabled":"1"}' http://127.0.0.1:5000/user

# curl -X POST -H "Content-Type: application/json" -d '{"username": "burner", "keycode": "1111", "doorlist":["topgarage"], "enabled":"1"}' http://127.0.0.1:5000/user

# curl -X POST -H "Content-Type: application/json" -d '{"username": "burner", "keycode": "1111", "doorlist":["topgarage",  "frontdoor", "bottomgarage"], "enabled":"1"}' http://127.0.0.1:5000/user
# Response:  {  "Status": "Added key" }

#allowed values are: topgarage, frontdoor, bottomgarage
#curl -X POST -H "Content-Type: application/json" -d '{"door":"topgarage", "pincode":"00003"}' http://127.0.0.1:5000/usekey
# Response:  {  "pin_correct": true}

#curl -X PUT -H "Content-Type: application/json" -d '{"door":"topgarage","status":"opened"}' http://127.0.0.1:5000/door/status
# Response:  { "door":"top garage", "status": "opened"}

#curl -X GET -H "Content-Type: application/json" -d '{"days":"10"}' http://127.0.0.1:5000/getlog
# Response:  {  log stuff in here }

# curl -X DELETE -H "Content-Type: application/json" -d '{"username":"mw"}' http://127.0.0.1:5000/user

# curl -X GET -H "Content-Type: application/json" -d '{"username":"max"}' http://127.0.0.1:5000/user

# curl -X POST -H "Content-Type: application/json" -d '{"username":"admin", "password":"password"}' http://127.0.0.1:5000/auth
#response = {
#  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIyMGU4OTg2NS0wNjM5LTQ3ZDEtYWU0YS1hYTg4ODQxNDIwNjciLCJleHAiOjE1MDg0NTU2NDgsImZyZXNoIjpmYWxzZSwiaWF0IjoxNTA4NDU0NzQ4LCJ0eXBlIjoiYWNjZXNzIiwibmJmIjoxNTA4NDU0NzQ4LCJpZGVudGl0eSI6ImFkbWluIn0.NT7t_17Hd3hT6_uTwy5FgGSN-koq8UeybEEKaLbRjIk",
#  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI2MWZmMDcxMC1hYjFlLTRhMTYtYTU1NS0yZjY0NjdlZDgyZjgiLCJleHAiOjE1MTEwNDY3NDgsImlhdCI6MTUwODQ1NDc0OCwidHlwZSI6InJlZnJlc2giLCJuYmYiOjE1MDg0NTQ3NDgsImlkZW50aXR5IjoiYWRtaW4ifQ.MMOMZCLxJbW9v2GwIgndtDZq_VpCKsueiqwXLgU04eg"
#}

#curl -X GET -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIyMGU4OTg2NS0wNjM5LTQ3ZDEtYWU0YS1hYTg4ODQxNDIwNjciLCJleHAiOjE1MDg0NTU2NDgsImZyZXNoIjpmYWxzZSwiaWF0IjoxNTA4NDU0NzQ4LCJ0eXBlIjoiYWNjZXNzIiwibmJmIjoxNTA4NDU0NzQ4LCJpZGVudGl0eSI6ImFkbWluIn0.NT7t_17Hd3hT6_uTwy5FgGSN-koq8UeybEEKaLbRjIk" http://127.0.0.1:5000/listallowed
import sys
import paho.mqtt.publish as publish
import re
import requests
import sql
import creds
from flask import Flask, request, jsonify
import json
from init import app, jwt
from flask_jwt_extended import jwt_required, \
    get_jwt_identity, get_jwt_claims

app.secret_key = creds.jwt_secret

def get_access_log(days):
    d = sql.get_doorlog(days)
    return d

def keycode_validation(keycode):
    if (len(keycode) > 3) and (len(keycode) < 11) and (re.match("^[A-D0-9]+$", keycode)):
        return True
    else:
        return False

@app.route("/")
@jwt_required
def hello():
    allowed = ['admin', 'user', 'sensor', 'python']
    if get_jwt_claims()['role'] in allowed:
        print request.headers
        return jsonify({"msg": "Hello World!"}), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403

@app.route("/listallowed", methods=['GET',])
@jwt_required
def list_allowed_keys():
    '''
    List doors with allowed users
    ["topgarage":["max", "mw", "etc"], "bottomgarage":[...]]
    '''
    allowed = ['admin']
    # print 'jwt claimes = '+str(get_jwt_claims())
    if get_jwt_claims()['role'] in allowed:
        return jsonify(sql.get_allowed()), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403


@app.route("/usekey", methods=['POST',])
@jwt_required
def usekey():
    allowed = ['admin', 'user', 'python']
    if get_jwt_claims()['role'] in allowed:
        try:
            content = request.get_json(silent=False)
            # print content
        except:
            print 'failed to get data'
        door = content['door']
        key = content['pincode']
        #use_key(pin, door)
        d = sql.validate_key(key, door)
        topic = 'doors/response/'+door
        if d is None:
            x = sql.insert_actionLog('Pinpad', door, key)
            resp = 0
            # mqtt.notify_door(0, door)
        else:
            if d == 'burner':
                # print 'user tested true for burner'
                sql.remove_disable_key(d)
            # print 'username = '+str(d)+' for '+door
            y = sql.insert_actionLog('Pinpad', door, key, d)
            # mqtt.notify_door(1, door)
            resp = 1
            publish.single(topic, resp, qos=2, auth=creds.mosq_auth, hostname=creds.broker)
            # resp = {'pin_correct':1}
        return jsonify({'pin_correct':resp}), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403

@app.route("/user", methods=['POST',])
@jwt_required
def add_user():
    print 'adding user'
    '''
    Add a new user to everything.
    '''
    allowed = ['admin']
    if get_jwt_claims()['role'] in allowed:
        print 'in here'
        content = request.get_json(silent=False)
        #{"username":invalid", "keycode":"invalid", "doorlist":["topgarage","frontdoor","bottomgarage"], "enabled":"1"}
        #{"username":pell", "password":"blah","keycode":"00003", "doorlist":["topgarage","frontdoor","bottomgarage"], "enabled":"1"}
        timeStart = None
        timeEnd = None
        doorlist = None
        if content.has_key('timeStart'):
            # print 'has time start'
            timeStart = content['timeStart'] # parse this to datetime in sql script
        else:
            content.update({'timeStart':0})
            # print 'making timeStart content = '+str(content)
        if content.has_key('timeEnd'):
            timeEnd = content['timeEnd'] # parse this to datetime in sql scrip
        else:
            content.update({'timeEnd':0})
        if len(content['keycode']) > 0:
            if not keycode_validation(content['keycode']):
                return jsonify({'status':'keycode failure'}), 200
        #sql.write_userdata(content)
        print content
        content['enabled'] = int(content['enabled'])
        print content
        return jsonify(sql.write_userdata(content)), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403

# @app.route("/auth/user/<username>", methods=['GET','POST'])
# @jwt_required
# def get_user_role(username):
#     '''
#
#     '''
#     allowed = ['admin', 'user', 'sensuser']
#     if get_jwt_claims()['role'] in allowed:
#         content = request.get_json(silent=False)
#         print content
#         password = content['password']
#         #password = request.json.get('password', None)
#         return jsonify(sql.auth_user(username, password)), 200
#     else:
#         return jsonify({"msg": "Forbidden"}), 403

@app.route("/user/data/<username>", methods=['GET',])
@jwt_required
def get_user_data(username):
    '''
    Receives: nothing
    Returns {'username':, 'keycode':, enabled:'', timeStart:, timeEnd, doors: [...]}
    '''
    allowed = ['admin']
    if get_jwt_claims()['role'] in allowed:
        # content = request.get_json(silent=False)
        # print content
        return jsonify(sql.fetch_user_data(username)), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403

@app.route("/user", methods=['PUT',])
@jwt_required
def update_user():
    # print 'udpating user'
    '''
    Select Username and update in user doorUsers table. Json must contain old username
    #{"old_username":"pell", "old_keycode":"1234", "username":pell", "keycode":"00003", "timeStart":"blah", "endTime":"blah", "doorlist":["topgarage","frontdoor","bottomgarage"], "enabled":"1"}

    curl -X PUT -H "Content-Type: application/json" -d '{"username":"max","keycode":"234A","enabled":"0","doorlist":["frontdoor", "bottomgarage"], "timeStart":"2017-09-11T03:03:27.860Z", "timeEnd":"2037-09-11T03:03:27.860Z"}' http://127.0.0.1:5000/user
    '''
    allowed = ['admin']
    if get_jwt_claims()['role'] in allowed:
        content = request.get_json(silent=False)
        # print content
        timeStart = None
        timeEnd = None
        doorlist = None
        if content.has_key('timeStart'):
            # print 'has time start'
            timeStart = content['timeStart'] # parse this to datetime
        else:
            content.update({'timeStart':0})
        if content.has_key('timeEnd'):
            timeEnd = content['timeEnd'] # parse this to datetime
        else:
            content.update({'timeEnd':0})
        if not keycode_validation(content['keycode']):
            return jsonify({'status':'keycode failure'}), 200
        return jsonify(sql.write_userdata(content)), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403

@app.route("/user/keycode", methods=['PUT',])
@jwt_required
def update_user_keycode():
    '''
    Select Username and update in user doorUsers table
    {"username":pell", "keycode":"00003"}
    '''
    allowed = ['admin', 'user']
    if get_jwt_claims()['role'] in allowed:
        content = request.get_json(silent=False)
        # print content
        if not keycode_validation(content['keycode']):
            return jsonify({'Status': 'Error', 'Message':'Keycode validation failure. Please try again'}), 200
        else:
            resp = sql.update_user(content['username'], 'keycode', content['keycode'])
            return jsonify(resp), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403

@app.route("/user/enabled", methods=['PUT',])
@jwt_required
def update_user_enabled():
    '''
    Select Username and update in user doorUsers table
    {"username":pell", "enabled":"1"}
    '''
    allowed = ['admin']
    if get_jwt_claims()['role'] in allowed:
        content = request.get_json(silent=False)
        return jsonify(sql.update_user(content['username'], 'enabled', int(content['enabled']))), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403

@app.route("/user/timeStart", methods=['PUT',])
@jwt_required
def update_user_timestart():
    '''
    Select Username and update in user doorUsers table
    '''
    allowed = ['admin', 'user']
    if get_jwt_claims()['role'] in allowed:
        content = request.get_json(silent=False)
        return jsonify(sql.update_user(content['username'], 'timeStart', content['timeStart'])), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403

@app.route("/user/timeEnd", methods=['PUT',])
@jwt_required
def update_user_timeend():
    '''
    Select Username and update in user doorUsers table
    '''
    allowed = ['admin', 'user']
    if get_jwt_claims()['role'] in allowed:
        content = request.get_json(silent=False)
        return jsonify(sql.update_user(content['username'], 'timeEnd', content['timeEnd'])), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403

@app.route("/user/doors", methods=['PUT',])
@jwt_required
def update_user_doors():
    '''
    Select Username and update canOpen table
    '''
    allowed = ['admin']
    if get_jwt_claims()['role'] in allowed:
        content = request.get_json(silent=False)
        return jsonify(sql.update_canOpen(content['username'], content['doors'])), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403

@app.route("/user/password", methods=['PUT',])
@jwt_required
def update_user_password():
    '''
    Select Username and update table
    '''
    allowed = ['admin', 'user', 'sensuser']
    if get_jwt_claims()['role'] in allowed:
        content = request.get_json(silent=False)
        return jsonify(sql.update_user(content['username'], 'password', content['password'])), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403

@app.route("/user/role", methods=['PUT',])
@jwt_required
def update_user_role():
    '''
    Select Username and update table
    '''
    allowed = ['admin']
    if get_jwt_claims()['role'] in allowed:
        content = request.get_json(silent=False)
        return jsonify(sql.update_user(content['username'], 'role', content['role'])), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403

@app.route("/users", methods=['GET',])
@jwt_required
def get_users():
    '''
    Returns [{'username':, 'keycode':, enabled:'', timeStart:, timeEnd, doors: [...]}, {...}, ...]
    '''
    allowed = ['admin']
    if get_jwt_claims()['role'] in allowed:
        return jsonify(sql.get_all_users()), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403

@app.route("/doors", methods=['GET',])
@jwt_required
def get_doors():
    '''
    Returns all possible door names in db as a list['door1','door2',...]
    '''
    allowed = ['admin', 'user']
    if get_jwt_claims()['role'] in allowed:
        content = request.get_json(silent=False)
        return jsonify(sql.get_all_doors()), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403

@app.route("/door/<door>", methods=['DELETE',])
@jwt_required
def del_door(door):
    '''
    Deletes <door>
    '''
    allowed = ['admin']
    if get_jwt_claims()['role'] in allowed:
        return jsonify(sql.del_door(door)), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403


@app.route("/door/setup", methods=['POST',])
@jwt_required
def setup_a_door():
    '''
    Post new door detail to DB
    Receives: {'door': 'topgarage'}
    Returns: {'Status': 'Success'/'Error'. 'Message': message}
    '''
    allowed = ['admin']
    if get_jwt_claims()['role'] in allowed:
        content = request.get_json(silent=False)
        door = content['door']
        return jsonify(sql.setup_door(door))
    else:
        return jsonify({"msg": "Forbidden"}), 403

@app.route("/door/status", methods=['GET',])
@jwt_required
def getStatus():
    allowed = ['admin', 'user']
    if get_jwt_claims()['role'] in allowed:
        content = request.get_json(silent=False)
        return jsonify(sql.get_doorstatus()), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403

@app.route("/door/status/<door>", methods=['GET',])
@jwt_required
def getADoorStatus(door):
    allowed = ['admin', 'user']
    if get_jwt_claims()['role'] in allowed:
        content = request.get_json(silent=False)
        return jsonify(sql.get_adoorstatus(door)), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403

@app.route("/door/log/<door>", methods=['POST',])
@jwt_required
def getLog(door):
    allowed = ['admin', 'user']
    if get_jwt_claims()['role'] in allowed:
        content = request.get_json(silent=False)
        # print content
        return jsonify(sql.get_doorlog(door, content)), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403

@app.route("/door/status", methods=['PUT',])
@jwt_required
def update_status():
    allowed = ['python']
    if get_jwt_claims()['role'] in allowed:
        content = request.get_json(silent=False)
        return jsonify(sql.update_doorstatus(content["status"], content['door'])), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403

@app.route("/getlog", methods=['GET',])
@jwt_required
def getAccessLog():
    '''
    curl -X GET -H "Content-Type: application/json" -d '{"days":"5"}' http://127.0.0.1:5000/getlog
    '''
    allowed = ['admin','user']
    if get_jwt_claims()['role'] in allowed:
        content = request.get_json(silent=False)
        resp = get_access_log(content['days'])
        return jsonify(resp), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403

try:
    sql.setup_admin_user(sys.argv[1], sys.argv[2])
except:
    pass

if __name__ == "__main__":
    app.run()
