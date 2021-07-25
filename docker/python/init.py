#!/usr/bin/env python3
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from flask_jwt_simple import JWTManager

app = Flask(__name__)
CORS(app)
jwt = JWTManager(app)
