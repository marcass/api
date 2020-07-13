#!/usr/bin/env python3
from datetime import datetime
from datetime import timedelta
from flask import Flask, request, jsonify
from flask_jwt_simple import (
    JWTManager, jwt_required, create_jwt, get_jwt_identity
)
import json
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

# Setup the Flask-JWT-Simple extension
# app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
jwt = JWTManager(app)
URL = 'http://kong:8000/jwt-stuff/consumers/'
# hostIP = '192.168.0.152'
# app.config['JWT_HEADER_TYPE'] = 'Bearer'

# Using the jwt_data_loader, we can change the values that
# will be present in the JWTs (that are made by the
# `create_jwt()` function). This will override everything
# currently in the token, so you will need to re-add
# the default claims (exp, iat, nbt, sub) if you still
# want them.
@jwt.jwt_data_loader
def add_claims_to_access_token(identity):
    global kong_stuff
    # print('printing identity')
    # print(identity)
    # if identity == 'admin':
    #     roles = 'admin'
    # else:
    #     roles = 'peasant'
    if 'admin' in kong_stuff['group']:
        roles = 'admin'
    else:
        roles = 'peasant'
    now = datetime.utcnow()
    return {
        'exp': now + timedelta(minutes=60),
        'iat': now,
        'nbf': now,
        'sub': {'username': identity},
        'roles': kong_stuff['group'],
        'iss': kong_stuff['key']
    }

@app.route('/auth/login', methods=['GET', 'POST'])
def auth():
    global kong_stuff
    #try:
    # print(request.headers)
    content = request.get_json(silent=False)
    # print(content)
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400
    # setup something to creat the user variable here
    print ('creds:')
    print (username)
    print (password)
    # user = 'test-user'
    # return jsonify(content), 200
    # get group
    #try:
    # in order to test do curl -i --user name:password http://localhost:8000/jwt-stuff/consuers/<name>/acls
    print('about to get group data')
    x = requests.get(URL+username+'/acls', auth=HTTPBasicAuth(username, password))
    #x = requests.get('https://skibo.duckdns.org/api/jwt-stuff/consumers/'+username+'/acls', auth=HTTPBasicAuth(username, password))
    print ('status code is: ')
    print (x.status_code)
    if x.status_code == 200:
        print('group get')
        print (x.text)
        data = json.loads(x.text)['data']
        print (data)
        group = []
        for i in data:
            if i['group']:
                group.append(i['group'])
        # group = data['data'][0]['group']
        # print('groups')
        print (group)
    else:
        print ('fucked up with a bad username')
        # print(x.status_code)
        return jsonify({"msg": x.status_code}), 401
    #except:
    #    print("couldn't get group")
    #    return jsonify({'Status':'Error', 'Message':'No group returned'}), 403
    #try:
    # get jwt stuff for making token
    r = requests.get(URL+username+'/jwt', auth=HTTPBasicAuth(username, password))
    #r = requests.get('https://skibo.duckdns.org/api/jwt-stuff/consumers/'+username+'/jwt', auth=HTTPBasicAuth(username, password))
    # r = requests.post('http://kong:8000/auth/'+username, json={'username': 'auth', 'password': 'iamauth'})
    if r.status_code == 200:
        print('jwt text')
        print (r.text)
        payload = json.loads(r.text)['data'][0]
        print('json loads of jwt text')
        print (payload)
        # fetch iss string
        kong_stuff = {'key': payload['key']}
        # set secret
        app.config['JWT_SECRET_KEY'] = payload['secret']
    else:
        # print 'fucked up with a bad username'
        print(r.status_code)
        return jsonify({"msg": r.status_code}), 401
    #except:
        #print("couldn't get jwt detail")
        #return jsonify({'Status':'Error', 'Message':'No jwt detail returned'}), 403
    kong_stuff.update({'group': group})
    # print('kong dict')
    # print (kong_stuff)
    # , 'refresh_token': create_refresh_token(identity=user)}
    ret = {'access_token': create_jwt(identity=username)}
    # print('token')
    # print (ret)
    return jsonify(ret), 200
    #except:
    #    print ('empty request')
    #    return jsonify({'Status':'Error', 'Message':'Empty request'})

if __name__ == "__main__":
    app.run(host = '0.0.0.0')
