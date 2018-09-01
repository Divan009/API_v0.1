from flask_restful import Resource, reqparse

from flask_jwt_extended import (
    get_jwt_identity,
    get_raw_jwt,
    jwt_required,
    get_jwt_claims,
    jwt_optional
)

from models.mapping import MappingModel
from models.investRequest import InvestRequestModel
from models.withdrawRequest import WithdrawRequestModel
from models.borrowRequest import BorrowRequestModel
from models.user import UserModel
from blacklist import BLACKLIST



class InvestOperations(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('req_id',
                        type = int,
                        required = True,
                        help = "req_id (required) error"
                        )
    @jwt_required
    def post(self):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'Admin privilege required.'}, 401

        data = InvestOperations.parser.parse_args()
        req = InvestRequestModel.find_by_id(data['req_id'])
        if req:
            user = UserModel.find_by_id(req.user_id)
        else:
            return {'error':'user request not found'}

        user.invest_amt = user.invest_amt + req.amount
        user.save_to_db()
        req.delete_from_db()
        return user.json()

    @jwt_required
    def get(self):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'Admin privilege required.'}, 401

        return {'investments': list(map(lambda x: x.json(), InvestRequestModel.find_all()))}

class WithdrawOperations(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('req_id',
                        type = int,
                        required = True,
                        help = "req_id (required) error"
                        )
    @jwt_required
    def post(self):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'Admin privilege required.'}, 401
        data = WithdrawOperations.parser.parse_args()
        req = WithdrawRequestModel.find_by_id(data['req_id'])
        if req:
            user = UserModel.find_by_id(req.user_id)
        else:
            return {'error':'user request not found'}

        user.invest_amt = user.invest_amt-req.amount
        user.save_to_db()
        req.delete_from_db()
        return user.json()

    @jwt_required
    def get(self):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'Admin privilege required.'}, 401

        return {'withdraw_request': list(map(lambda x: x.json(), WithdrawRequestModel.find_all()))}

class BorrowOperations(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('req_id',
                        type = int,
                        required = True,
                        help = "req_id (required) error"
                        )
    @jwt_required
    def post(self):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'Admin privilege required.'}, 401
        data = BorrowOperations.parser.parse_args()
        req = BorrowRequestModel.find_by_id(data['req_id'])

        user = UserModel.find_by_id(req.user_id)
        interest = int(req.amount * (3/100))

        if user:
            if user.borrow_amt == 0 and req.amount+interest<user.invest_amt:

                lender = UserModel.find_investor(req.amount,user.username)
                if lender:
                    lender.lend_amt = lender.lend_amt + req.amount
                    lender.interest_amt_L = lender.interest_amt_L+interest
                    lender.invest_amt = lender.invest_amt - req.amount
                    user.borrow_amt = req.amount
                    user.interest_amt_B = interest
                    lender.weight_id = lender.weight_id+1
                    transaction = MappingModel(lender.id,user.id)
                else:
                    return {'message':'sorry no investor found'}

            else:
                return {'message':'error USER operation not allowed'}

            transaction.save_to_db()
            user.Trx_id = transaction.Trx_id
            user.save_to_db()
            lender.save_to_db()
            req.delete_from_db()
            return user.json()
        return {'error':'user does not exist'}

    @jwt_required
    def get(self):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'Admin privilege required.'}, 401

        return {'borrow_request': list(map(lambda x: x.json(), BorrowRequestModel.find_all()))}
