#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_jwt_extended import jwt_required, \
    create_access_token, jwt_refresh_token_required, \
    create_refresh_token, get_jwt_identity, get_jwt_claims
import json
import requests
from init import app, jwt

app.secret_key = '09q785349hangpoiqa5984'  # Change this!
app.config['JWT_HEADER_TYPE'] = 'Bearer'

@app.route('/auth/login', methods=['POST'])
def auth():
    try:
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        print (username)
        print (password)
        # get user detail from kong auth route
        r = requests.post('http://kong:8000/auth/'+username, json={'username': 'auth', 'password': 'iamauth'})
        if r.status_code == 200:
            print (r.text)
            ret = {'access_token': create_access_token(identity=user), 'refresh_token': create_refresh_token(identity=user)}
            print (ret)
            return jsonify(ret), 200
        else:
            # print 'fucked up with a bad username'
            return jsonify({"msg": "Bad username or password"}), 401
    except:
        print ('empty request')
        return jsonify({'Status':'Error', 'Message':'Empty request'})

if __name__ == "__main__":
    app.run(host= '0.0.0.0')
