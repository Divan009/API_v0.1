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

from models.investRequest import InvestRequestModel
from models.withdrawRequest import WithdrawRequestModel
from models.borrowRequest import BorrowRequestModel
from models.user import UserModel
from models.mapping import MappingModel
from blacklist import BLACKLIST

class all_investment(Resource):
    def get(self):
        return {'investments': list(map(lambda x: x.json(), UserModel.query.all()))}

class server_status(Resource):
    def get(self):
        return {'status':'online'}

#user
class InvestRequest(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('amt',
                        type = int,
                        required = True,
                        help = "invest_amt(required) error"
                        )
    parser.add_argument('options',
                        type = str,
                        required = True,
                        help = "option required"
                        )

    @jwt_required
    def post(self):
        data = InvestRequest.parser.parse_args()
        user_id = get_jwt_identity()
        user = UserModel.find_by_id(user_id)

        if data['options'] == 'add':
            order_id = 'PK'+str(data['amt'])+'LD'+str(random.randint(1,10001))+'XI'
            request = InvestRequestModel(user.id,data['amt'],order_id,0)
            ''' further work require security breach '''
            request.save_to_db()
            return {'message':'successful'}

        elif data['options'] == 'cancel':
            request = InvestRequestModel.find_by_Userid(user_id)
            if request:
                request.delete_from_db()
            return {'message':'request cancelled'}, 200


    @jwt_required
    def get(self):
        user_id = get_jwt_identity()
        user = UserModel.find_by_id(user_id)
        req = InvestRequestModel.find_by_Userid(user.id)
        if req:
            return req.json(), 200
        return {'error':'no invest request'}, 401

class WithdrawRequest(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('amt',
                        type = int,
                        required = True,
                        help = "amount (required) error"
                        )
    parser.add_argument('options',
                        type = str,
                        required = True,
                        help = "option required"
                        )
    @jwt_required
    def post(self):
        user_id = get_jwt_identity()
        user = UserModel.find_by_id(user_id)
        data = WithdrawRequest.parser.parse_args()

        if data['options'] == 'add':
            if user.borrow_amt == 0 and user.invest_amt >= data['amt']:
                order_id = 'PK'+str(data['amt'])+'LD'+str(random.randint(1,10001))+'XI'
                request = WithdrawRequestModel(user.id,data['amt'],order_id,0)
                request.save_to_db()
                return {'message':'successful'}
            else:
                return {'error':999}

        elif data['options'] == 'cancel':
            request = WithdrawRequestModel.find_by_Userid(user_id)
            if request:
                request.delete_from_db()
            return {'message':'request cancelled'}, 200


    @jwt_required
    def get(self):
        user_id = get_jwt_identity()
        user = UserModel.find_by_id(user_id)
        req = WithdrawRequestModel.find_by_Userid(user.id)
        if req:
            return req.json(), 200
        return {'error':'no withdraw request'}, 401

class borrowRequest(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('amt',
                        type = int,
                        required = True,
                        help = "borrow_amt(required) error"
                        )
    parser.add_argument('options',
                        type = str,
                        required = True,
                        help = "option required"
                        )
    @jwt_required
    def post(self):
        user_id = get_jwt_identity()
        user = UserModel.find_by_id(user_id)
        data = borrowRequest.parser.parse_args()
        interest = int(data['amt']*(3/100))

        if data['options'] == 'add':
            if user.borrow_amt == 0 and data['amt']+interest<user.invest_amt:
                order_id = 'PK'+str(data['amt'])+'LD'+str(random.randint(1,10001))+'XI'
                request = BorrowRequestModel(user.id,data['amt'],order_id,0)
                request.save_to_db()
                return {'message':'successful'}
            else:
                return {'error':999}

        elif data['options'] == 'cancel':
            request = BorrowRequestModel.find_by_Userid(user_id)
            if request:
                request.delete_from_db()
            return {'message':'request cancelled'}, 200

    @jwt_required
    def get(self):
        user_id = get_jwt_identity()
        user = UserModel.find_by_id(user_id)
        req = BorrowRequestModel.find_by_Userid(user.id)
        if req:
            return req.json(), 200
        return {'error':'no borrow request'}, 401

class Repay(Resource):
    @jwt_required
    def get(self):
        user_id = get_jwt_identity()
        user = UserModel.find_by_id(user_id)

        if user:
            transaction = MappingModel.find_by_id(user.Trx_id)

            if transaction and transaction.b_id == user.id:
                l_id = transaction.l_id
                b_id = transaction.b_id

                lender = UserModel.find_by_id(l_id)
                borrower = UserModel.find_by_id(b_id)

                borrower.invest_amt = borrower.invest_amt - (borrower.borrow_amt+borrower.interest_amt_B)
                lender.invest_amt = lender.invest_amt + (borrower.borrow_amt + borrower.interest_amt_B)
                lender.lend_amt = lender.lend_amt - borrower.borrow_amt
                lender.interest_amt_L = lender.interest_amt_L - borrower.interest_amt_B

                borrower.borrow_amt = 0
                borrower.interest_amt_B = 0
                borrower.Trx_id = None
                transaction.delete_from_db()
                lender.save_to_db()
                borrower.save_to_db()

            else:
                return {'error':999}

            return {'message':'repayment successful'}





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
            return {'error':'user already exist'}, 401
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
