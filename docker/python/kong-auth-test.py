#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_jwt_extended import jwt_required, \
    create_access_token, jwt_refresh_token_required, \
    create_refresh_token, get_jwt_identity, get_jwt_claims
import json
import requests
from init import app, jwt

app.secret_key = 09q785349hangpoiqa5984  # Change this!
app.config['JWT_HEADER_TYPE'] = 'Bearer'

@app.route('/auth/login', methods=['POST'])
def auth():
    try:
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        print (username)
        print (password)
        # get user detail from kong auth route
        r = requests.get('http://kong:8001/'+username)
        print (r.text)
        ret = {'access_token': create_access_token(identity=user), 'refresh_token': create_refresh_token(identity=user)}
        return jsonify(ret), 200
                                                                                                                                                                                                                                                                                    else:
                                                                                                                                                                                                                                                                                                    # print 'fucked up with a bad username'
                                                                                                                                                                                                                                                                                                            return jsonify({"msg": "Bad username or password"}), 401
                                                                                                                                                                                                                                                                                                            except:
                                                                                                                                                                                                                                                                                                                        print 'empty request'
                                                                                                                                                                                                                                                                                                                            return jsonify({'Status':'Error', 'Message':'Empty request'})

@app.route("/auth", methods=['POST',])
def post_test():
    '''
    JWT generator test
    '''
    print ("headers are:")
    print (request.headers)
    content = request.get_json(silent=False)
    print (content)

    return jsonify(content), 200

@app.route("/auth/hello", methods=['GET',])
def get_test():
    '''
    Get test
    '''
    print ("headers are:")
    print (request.headers)
    content = {'msg': 'This is what you get with kong'} 
    print("Hello thre konga")
    return jsonify(content), 200

if __name__ == "__main__":
    app.run(host= '0.0.0.0')
