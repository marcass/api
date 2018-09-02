# Mostly obtained from:
# https://github.com/vimalloc/flask-jwt-extended
# also check out: https://gist.github.com/jslvtr/139cf76db7132b53f2b20c5b6a9fa7ad
import sql
from flask import Flask, request, jsonify
from flask_jwt_extended import jwt_required, \
    create_access_token, jwt_refresh_token_required, \
    create_refresh_token, get_jwt_identity, get_jwt_claims

from init import app, jwt
import creds

app.secret_key = creds.jwt_secret  # Change this!
app.config['JWT_HEADER_TYPE'] = 'Bearer'


# http://flask-jwt-extended.readthedocs.io/en/latest/tokens_from_complex_object.html
# Create a function that will be called whenever create_access_token
# is used. It will take whatever object is passed into the
# create_access_token method, and lets us define what custom claims
# should be added to the access token.
@jwt.user_claims_loader
def add_claims_to_access_token(user):
    if 'sites' in user:
        return {'role': user['role'], 'sites':user['sites']}
    else:
        return {'role': user['role']}


# Create a function that will be called whenever create_access_token
# is used. It will take whatever object is passed into the
# create_access_token method, and lets us define what the identity
# of the access token should be.
@jwt.user_identity_loader
def user_identity_lookup(user):
    return user['username']

@app.route('/auth/login', methods=['POST'])
def auth():
    try:
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        # print username
        # print password
        content = sql.auth_user(username, password)
        # print content
        if content['status'] == 'passed':
            # Create user and role object
            if 'sites' in content:
                user = {'username':username, 'role':content['role'], 'sites':content['sites']}
            else:
                user = {'username':username, 'role':content['role']}
            # print 'user = '+str(user)
            # if 'sites' in content['role']:
            #     user = {'username':username, 'role':content['role']['role'], 'sites': content['role']['sites']}
            # else:
            #     user = {'username':username, 'role':content['role']['role']}
            # Use create_access_token() and create_refresh_token() to create our
            # access and refresh tokens
            ret = {
                'access_token': create_access_token(identity=user),
                'refresh_token': create_refresh_token(identity=user), 'data':{
                'role': content['role']}
            }
            # print ret
            return jsonify(ret), 200
        else:
            # print 'fucked up with a bad username'
	    return jsonify({"msg": "Bad username or password"}), 401
    except:
        print 'empty request'
	return jsonify({'Status':'Error', 'Message':'Empty request'})

@app.route('/auth/user', methods=['POST'])
@jwt_required
def add_user():
    '''
    Add a new user to auth table
    '''
    allowed = ['admin']
    print 'jwt claims are '+str(get_jwt_claims())
    if get_jwt_claims()['role'] in allowed:
        try:
            username = request.json.get('username', None)
            password = request.json.get('password', None)
            role = request.json.get('role', None)
            # print username
            # print password
            if sql.setup_user(username, password, role):
                return jsonify({'Status':'Success', 'Message':'User '+username+' successfully added'}), 200
            else:
                # print 'fucked up with a bad username'
    	        return jsonify({'Status':'Error', 'Message':'Bad username'}), 400
        except:
            return jsonify({'Status':'Error', 'Message':'Adding user '+username+' failed'}), 400
    else:
       return jsonify({"msg": "Forbidden"}), 403

@app.route("/auth/user/password", methods=['PUT',])
@jwt_required
def update_user_password():
    '''
    Select Username and update pass
    '''
    allowed = ['admin', 'user', 'sensuser']
    if get_jwt_claims()['role'] in allowed:
        content = request.get_json(silent=False)
        return jsonify(sql.update_user(content['username'], 'password', content['password'])), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403

@app.route("/auth/user/<username>", methods=['GET', 'POST'])
@jwt_required
def get_user_role(username):
    '''
    Authenitcate a user as being in DB and return role
    '''
    allowed = ['admin', 'user', 'sensuser']
    if get_jwt_claims()['role'] in allowed:
        content = request.get_json(silent=False)
        # print content
        password = content['password']
        #password = request.json.get('password', None)
        return jsonify(sql.auth_user(username, password)), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403

@app.route("/auth/user/<username>", methods=['DELETE',])
@jwt_required
def remove_user(username):
    '''
    Remove Username in user doorUsers table, and update all tables...
    {'username':'mw'}
    '''
    allowed = ['admin']
    if get_jwt_claims()['role'] in allowed:
        return jsonify(sql.delete_user(username)), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403

# The jwt_refresh_token_required decorator insures a valid refresh
# token is present in the request before calling this endpoint. We
# can use the get_jwt_identity() function to get the identity of
# the refresh token, and use the create_access_token() function again
# to make a new access token for this identity.
@app.route('/auth/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    ret = {
        'access_token': create_access_token(identity=current_user)
    }
    return jsonify(ret), 200

@jwt.expired_token_loader
def my_expired_token_callback():
    return jsonify({
        'status': 401,
        'sub_status': 101,
        'msg': 'The token has expired'
    }), 401

if __name__ == "__main__":
    app.run()
