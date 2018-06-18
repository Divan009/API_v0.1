from flask_restful import Resource, reqparse
from models.user import UserModel

class InvestOperations(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('id',
                        type=int,
                        required=True,
                        help="ID(required) error "
                        )
    parser.add_argument('invest_amt',
                        type = int,
                        required = True,
                        help = "invest_amt(required) error"
                        )
    def post(self):
        data = InvestOperations.parser.parse_args()
        user = UserModel.find_by_id(data['id'])
        if user:
            user.invest_amt = user.invest_amt + data['invest_amt']
        else:
            user = UserModel(data['invest_amt'])

        user.save_to_db()
        return user.json()

class all_investment(Resource):
    def get(self):
        return {'investments': list(map(lambda x: x.json(), UserModel.query.all()))}
