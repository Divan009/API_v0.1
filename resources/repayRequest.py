from flask_restful import Resource, reqparse

from flask_jwt_extended import (
    get_jwt_identity,
    get_raw_jwt,
    jwt_required,
    get_jwt_claims,
    jwt_optional
)

from models.mapping import MappingModel
from models.repayRequest import RepayRequestModel
from models.user import UserModel
from blacklist import BLACKLIST

class all_repayRequest(Resource):
    @jwt_required
    def get(self):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'Admin privilege required.'}, 401

        return {'request': list(map(lambda x: x.json(), RepayRequestModel.find_all()))}


class repay(Resource):
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

        data = repay.parser.parse_args()
        req = RepayRequestModel.find_by_id(data['req_id'])
        user = UserModel.find_by_id(req.user_id)
        transaction = MappingModel.find_by_id(user.Trx_id)

        if transaction and transaction.b_id == user.id:
            l_id = transaction.l_id
            b_id = transaction.b_id

            lender = UserModel.find_by_id(l_id)
            borrower = UserModel.find_by_id(b_id)

            lender.invest_amt = lender.invest_amt + borrower.borrow_amt
            lender.lend_amt = lender.lend_amt - borrower.borrow_amt

            borrower.borrow_amt = 0
            borrower.Trx_id = None



        else:
            return {'message':'error_USER no such transaction'}

        transaction.delete_from_db()
        lender.save_to_db()
        borrower.save_to_db()

        return borrower.json()
