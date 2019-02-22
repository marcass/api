#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_jwt_extended import jwt_required, \
    create_access_token, jwt_refresh_token_required, \
    create_refresh_token, get_jwt_identity, get_jwt_claims
import json
import requests
from requests.auth import HTTPBasicAuth
from init import app, jwt

# app.secret_key = '09q785349hangpoiqa5984'  # Change this!
app.config['JWT_HEADER_TYPE'] = 'Bearer'

# Using the user_claims_loader, we can specify a method that will be
# called when creating access tokens, and add these claims to the said
# token. This method is passed the identity of who the token is being
# created for, and must return data that is json serializable
@jwt.user_claims_loader
def add_claims_to_access_token(identity):
    global key
    return {
        'iss': key
    }

@app.route('/auth/login', methods=['GET', 'POST'])
def auth():
    global key
    # try:
    content = request.get_json(silent=False)
    print(content)
    username = request.json.get('username', None)
    password = request.json.get('password', None)
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
        else:
            # print 'fucked up with a bad username'
            print(r.status_code)
            return jsonify({"msg": r.status_code}), 401
    except:
        print("couldn't get jwt detail")
        return jsonify({'Status':'Error', 'Message':'No jwt detail returned'}), 403
    print (payload)
    print(payload['secret'])
    app.secret_key = payload['secret']
    print(payload['key'])
    key = payload['key']
    user_data = {'username': username, 'group': group}
    # , 'refresh_token': create_refresh_token(identity=user)}
    ret = {'access_token': create_access_token(identity=user_data)}
    print (ret)
    return jsonify(ret), 200
    # except:
    #     print ('empty request')
    #     return jsonify({'Status':'Error', 'Message':'Empty request'})

if __name__ == "__main__":
    app.run(host= '0.0.0.0')


# r = requests.post(api_URL, auth=HTTPBasicAuth('user', 'pass'), data=payload)
