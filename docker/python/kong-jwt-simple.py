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
    print(identity)
    if identity == 'admin':
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
    # try:
    content = request.get_json(silent=False)
    print(content)
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400
    # setup something to creat the user variable here
    print (username)
    print (password)
    # user = 'test-user'
    # return jsonify(content), 200
    # get group
    try:
        x = requests.get('http://localhost:8000/jwt-stuff/'+username+'/acls', auth=HTTPBasicAuth(username, password))
        if x.status_code == 200:
            print (x.text)
            data = json.loads(x.text)
            group = data['data'][0]['group']
            print (group)
        else:
            # print 'fucked up with a bad username'
            print(x.status_code)
            return jsonify({"msg": x.status_code}), 401
    except:
        print("couldn't get group")
        return jsonify({'Status':'Error', 'Message':'No group returned'}), 403
    try:
        # get jwt stuff for making token
        # assumes route setup in kong that allows a path of jwt, with a service that has un upstram path of /consumers
        r = requests.get('http://localhost:8000/jwt-stuff/'+username+'/jwt', auth=HTTPBasicAuth(username, password))
        # r = requests.post('http://kong:8000/auth/'+username, json={'username': 'auth', 'password': 'iamauth'})
        if r.status_code == 200:
            print (r.text)
            payload = json.loads(r.text)['data'][0]
            print (payload)
            # fetch iss string
            kong_stuff = {'key': payload['key']}
            # set secret
            app.config['JWT_SECRET_KEY'] = payload['secret']
        else:
            # print 'fucked up with a bad username'
            print(r.status_code)
            return jsonify({"msg": r.status_code}), 401
    except:
        print("couldn't get jwt detail")
        return jsonify({'Status':'Error', 'Message':'No jwt detail returned'}), 403
    kong_stuff.update({'group': group})
    print (kong_stuff)
    # , 'refresh_token': create_refresh_token(identity=user)}
    ret = {'access_token': create_jwt(identity=username)}
    print (ret)
    return jsonify(ret), 200
    # except:
    #     print ('empty request')
    #     return jsonify({'Status':'Error', 'Message':'Empty request'})

if __name__ == "__main__":
    app.run(host = '0.0.0.0')
