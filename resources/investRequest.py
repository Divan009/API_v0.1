from flask_restful import Resource, reqparse

from flask_jwt_extended import (
    get_jwt_identity,
    get_raw_jwt,
    jwt_required,
    get_jwt_claims,
    jwt_optional
)

from models.investRequest import InvestRequestModel
from models.user import UserModel
from blacklist import BLACKLIST

class all_investRequest(Resource):
    @jwt_required
    def get(self):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'Admin privilege required.'}, 401

        return {'investments': list(map(lambda x: x.json(), InvestRequestModel.find_all()))}

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
