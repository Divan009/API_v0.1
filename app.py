import os
from flask import Flask,jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from blacklist import BLACKLIST

from resources.user import InvestRequest,RepayRequest,WithdrawRequest,borrow,UserRegister,UserLogin,UserLogout,TokenRefresh,all_investment,User_info
from resources.investRequest import all_investRequest,InvestOperations
from resources.repayRequest import all_repayRequest,repay
from resources.withdrawRequest import all_withdrawRequest,verifyWithdraw

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'TEMP_TEST_XXXXX362357_SECRET_KEY'

api = Api(app)

app.config['JWT_BLACKLIST_ENABLED'] = True  # enable blacklist feature
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']  # allow blacklisting for access and refresh tokens
jwt = JWTManager(app)

@jwt.user_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1:   # instead of hard-coding, we should read from a config file to get a list of admins instead
        return {'is_admin': True}
    return {'is_admin': False}


# This method will check if a token is blacklisted, and will be called automatically when blacklist is enabled
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token['jti'] in BLACKLIST


# The following callbacks are used for customizing jwt response/error messages.
# The original ones may not be in a very pretty format (opinionated)
@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
        'message': 'The token has expired.',
        'error': 'token_expired'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):  # we have to keep the argument here, since it's passed in by the caller internally
    return jsonify({
        'message': 'Signature verification failed.',
        'error': 'invalid_token'
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        "description": "Request does not contain an access token.",
        'error': 'authorization_required'
    }), 401

@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return jsonify({
        "description": "The token is not fresh.",
        'error': 'fresh_token_required'
    }), 401

@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({
        "description": "The token has been revoked.",
        'error': 'token_revoked'
    }), 401
# JWT configuration ends

@app.before_first_request
def create_tables():
    db.create_all()

#deposit and withdraw request endpoint
api.add_resource(InvestRequest,'/invest')
api.add_resource(WithdrawRequest,'/withdraw')

#investment endpointd
api.add_resource(all_investment,'/everything')
api.add_resource(borrow,'/borrow')
api.add_resource(RepayRequest,'/repay')

#user endpoints
api.add_resource(User_info,'/user_info')
api.add_resource(UserRegister,'/register')
api.add_resource(UserLogin,'/login')
api.add_resource(UserLogout,'/logout')
api.add_resource(TokenRefresh,'/refresh_token')

#admin only

#invest
api.add_resource(all_investRequest,'/all_investRequest')
api.add_resource(InvestOperations,'/verifyInvest')
#repay
api.add_resource(all_repayRequest,'/all_repayRequest')
api.add_resource(repay,'/verifyRepay')
#withdraw
api.add_resource(all_withdrawRequest,'/all_withdrawRequest')
api.add_resource(verifyWithdraw,'/verifyWithdraw')


if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(host='0.0.0.0',threaded=True,port=5000, debug=True)
