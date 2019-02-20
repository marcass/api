#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_jwt_extended import jwt_required, \
    create_access_token, jwt_refresh_token_required, \
    create_refresh_token, get_jwt_identity, get_jwt_claims
import json
import requests
from requests.auth import HTTPBasicAuth
from init import app, jwt

app.secret_key = '09q785349hangpoiqa5984'  # Change this!
app.config['JWT_HEADER_TYPE'] = 'Bearer'

@app.route('/auth/login', methods=['POST'])
def auth():
    try:
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        # setup something to creat the user variable here
        print (username)
        print (password)
        # assumes route setup in kong that allows a path of jwt, with a service that has un upstram path of /consumers
        r = requests.get('http://localhost:8000/jwt/'+user+'/jwt', auth=HTTPBasicAuth(username, password))
        # r = requests.post('http://kong:8000/auth/'+username, json={'username': 'auth', 'password': 'iamauth'})
        if r.status_code == 200:
            print (r.text)
            ret = {'access_token': create_access_token(identity=r.text)}
            # , 'refresh_token': create_refresh_token(identity=user)}
            print (ret)
            return jsonify(ret), 200
        else:
            # print 'fucked up with a bad username'
            print(r.status_code)
            return jsonify({"msg": "Bad username or password"}), 401
    except:
        print ('empty request')
        return jsonify({'Status':'Error', 'Message':'Empty request'})

if __name__ == "__main__":
    app.run(host= '0.0.0.0')


# r = requests.post(api_URL, auth=HTTPBasicAuth('user', 'pass'), data=payload)
