import random
from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    get_raw_jwt,
    jwt_required,
    jwt_optional
)

from models.repayRequest import RepayRequestModel
from models.investRequest import InvestRequestModel
from models.withdrawRequest import WithdrawRequestModel
from models.user import UserModel
from models.mapping import MappingModel
from blacklist import BLACKLIST

class all_investment(Resource):
    def get(self):
        return {'investments': list(map(lambda x: x.json(), UserModel.query.all()))}



#user
class InvestRequest(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('invest_amt',
                        type = int,
                        required = True,
                        help = "invest_amt(required) error"
                        )

    @jwt_required
    def post(self):
        data = InvestRequest.parser.parse_args()
        '''
        if len(str(data['UTR'])) != 12:
            return {'error':'UPI reference is not 12 digits'}
        '''


        user_id = get_jwt_identity()
        user = UserModel.find_by_id(user_id)

        order_id = 'PK'+str(data['invest_amt'])+'LD'+str(random.randint(1,101))+'OI'
        request = InvestRequestModel(user.id,data['invest_amt'],order_id,0)

        request.save_to_db()
        return {'order_id':order_id}

class RepayRequest(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('UTR',
                        type = int,
                        required = True,
                        help = "UTR (required) error"
                        )
    @jwt_required
    def post(self):
        data = RepayRequest.parser.parse_args()
        if len(str(data['UTR'])) != 12:
            return {'error':'UPI reference is not 12 digits'}

        user_id = get_jwt_identity()
        user = UserModel.find_by_id(user_id)

        if user.borrow_amt == 0:
            return {'error':'operation invalid'}

        request = RepayRequestModel(user.id,user.borrow_amt,data['UTR'])
        request.save_to_db()
        return {'message':'repay request submitted Successfully'}

class WithdrawRequest(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('amount',
                        type = int,
                        required = True,
                        help = "amount (required) error"
                        )
    @jwt_required
    def post(self):
        user_id = get_jwt_identity()
        user = UserModel.find_by_id(user_id)
        data = WithdrawRequest.parser.parse_args()
        if user.borrow_amt == 0 and user.invest_amt >= data['amount']:
            withdraw_request = WithdrawRequestModel(user.id,data['amount'])
        else:
            return {'error':'operation not allowed'}
        withdraw_request.save_to_db()
        return {'message':'request submitted successfully'}


class borrow(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('borrow_amt',
                        type = int,
                        required = True,
                        help = "borrow_amt(required) error"
                        )
    @jwt_required
    def post(self):
        data = borrow.parser.parse_args()
        user_id = get_jwt_identity()
        user = UserModel.find_by_id(user_id)
        if user:
            if user.borrow_amt == 0 and data['borrow_amt']<user.invest_amt:
                #user.borrow_amt = data['borrow_amt'] #changes required
                lender = UserModel.find_investor(data['borrow_amt'],user.username)
                if lender:
                    lender.lend_amt = lender.lend_amt+data['borrow_amt']
                    lender.invest_amt = lender.invest_amt - data['borrow_amt']
                    user.borrow_amt = data['borrow_amt']
                    lender.weight_id = lender.weight_id + 1
                    transaction = MappingModel(lender.id,user.id)
                else:
                    return {'message':'sorry no investor found'}

            else:
                return {'message':'error_USER operation not allowed'}
            transaction.save_to_db()
            user.Trx_id = transaction.Trx_id
            user.save_to_db()
            lender.save_to_db()
            return user.json()
        return {'error':'user does not exist'}


class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
                        type=str,
                        required=True,
                        help="username (required) error "
                        )
    parser.add_argument('password',
                        type = str,
                        required = True,
                        help = "password (required) error"
                        )
    def post(self):
        data = UserRegister.parser.parse_args()
        user = UserModel.find_by_username(data['username'])
        if user:
            return {'error':'user already exist'}, 200
        else:
            user = UserModel(data['username'],data['password'])
        user.save_to_db()
        return {'message':'user created successfully'}, 200

class UserLogin(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
                        type=str,
                        required=True,
                        help="username (required) error "
                        )
    parser.add_argument('password',
                        type = str,
                        required = True,
                        help = "password (required) error"
                        )
    def post(self):
        data = UserRegister.parser.parse_args()
        user = UserModel.find_by_username(data['username'])

        if user and safe_str_cmp(user.password,data['password']):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {
                       'access_token': access_token,
                       'refresh_token': refresh_token
                   }, 200

        return {"message": "Invalid Credentials!"}, 401

class User_info(Resource):
    @jwt_required
    def get(self):
        user_id = get_jwt_identity()
        user = UserModel.find_by_id(user_id)
        return user.json(), 200



class UserLogout(Resource):
    @jwt_required
    def get(self):
        jti = get_raw_jwt()['jti']
        BLACKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200

class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def get(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}, 200
