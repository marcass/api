#!/usr/bin/env python3
from flask import Flask, request, jsonify
import json
import jwt

from init import app

@app.route("/flask/data", methods=['POST',])
def post_test():
    '''
    Post test
    '''
    print ("headers are:")
    print (request.headers)
    content = request.get_json(silent=False)
    print (content)
    return jsonify(content), 200

@app.route("/flask/hello", methods=['GET',])
def get_test():
    '''
    Get test
    '''
    token = request.headers['Authorization'].split( )[1]
    print (token)
    claims = jwt.decode(token, verify=False)
    print (claims)
    roles = claims['roles']
    print (roles)
    username = claims['sub']['username']
    print(username)
    content = {'msg': 'This is what you get with kong'}
    print("Hello thre konga")
    return jsonify(content), 200

if __name__ == "__main__":
    app.run(host= '0.0.0.0')
