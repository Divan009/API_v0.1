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
from models.user import UserModel
from models.mapping import MappingModel
from blacklist import BLACKLIST

'''
class all_investment(Resource):
    @jwt_optional
    def get(self):
        #return {'investments': list(map(lambda x: x.json(), UserModel.query.all()))}
        user_id = get_jwt_identity()
        user = UserModel.find_all()
        if user_id:
            return user.json(), 200

        return{
            'username':[items['username'] for item in items],
            'message':'More data on login'
        }
'''

class InvestOperations(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('invest_amt',
                        type = int,
                        required = True,
                        help = "invest_amt(required) error"
                        )
    @jwt_required
    def post(self):
        data = InvestOperations.parser.parse_args()
        #user = UserModel.find_by_username(data['username'])
        user_id = get_jwt_identity()
        user = UserModel.find_by_id(user_id)
        if user:
            user.invest_amt = user.invest_amt + data['invest_amt']
        else:
            return {'error':'user not registerd '}

        user.save_to_db()
        return user.json()


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
                lender.lend_amt = data['borrow_amt']
                lender.invest_amt = lender.invest_amt - lender.lend_amt
                user.borrow_amt = data['borrow_amt']
                transaction = MappingModel(lender.id,user.id)

            else:
                return {'message':'error_USER operation not allowed'}
            transaction.save_to_db()
            lender.Trx_id = transaction.Trx_id
            user.Trx_id = transaction.Trx_id
            user.save_to_db()
            lender.save_to_db()
            return user.json()
        return {'error':'user does not exist'}


class repay(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('transaction',
                        type = int,
                        required = True,
                        help = "error: transaction id required for repayment"
                        )
    @jwt_required
    def post(self):
        data = repay.parser.parse_args()
        transaction = MappingModel.find_by_id(data['transaction'])
        user_id = get_jwt_identity()
        if transaction and transaction.b_id == user_id:
            l_id = transaction.l_id
            b_id = transaction.b_id

            lender = UserModel.find_by_id(l_id)
            borrower = UserModel.find_by_id(b_id)

            lender.invest_amt = lender.invest_amt + lender.lend_amt
            lender.lend_amt = 0
            lender.Trx_id = None

            borrower.borrow_amt = 0
            borrower.Trx_id = None

        else:
            return {'message':'error_USER no such transaction'}

        transaction.delete_from_db()
        lender.save_to_db()
        borrower.save_to_db()

        return borrower.json()


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
            return {'error':'user already exist'}
        else:
            user = UserModel(data['username'],data['password'])
        user.save_to_db()
        return user.json()

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

class UserLogout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        BLACKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200

class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}, 200
