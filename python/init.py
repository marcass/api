from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

import sql
sql.setup_db()

app = Flask(__name__)
CORS(app)
