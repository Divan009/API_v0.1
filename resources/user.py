from flask_restful import Resource, reqparse
from models.user import UserModel
from models.mapping import MappingModel



class all_investment(Resource):
    def get(self):
        return {'investments': list(map(lambda x: x.json(), UserModel.query.all()))}



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



class borrow(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('id',
                        type=int,
                        required=True,
                        help="ID(required) error "
                        )
    parser.add_argument('borrow_amt',
                        type = int,
                        required = True,
                        help = "borrow_amt(required) error"
                        )
    def post(self):
        data = borrow.parser.parse_args()
        user = UserModel.find_by_id(data['id'])
        if user:
            if user.borrow_amt == 0 and data['borrow_amt']<user.invest_amt:
                #user.borrow_amt = data['borrow_amt'] #changes required
                lender = UserModel.find_investor(data['borrow_amt'],data['id'])
                '''print("lender.id: ")
                print(lender.id)
                print("user.id: ")'''
                print(user.id)
                lender.lend_amt = data['borrow_amt']
                lender.invest_amt = lender.invest_amt - lender.lend_amt
                user.borrow_amt = data['borrow_amt']
                transaction = MappingModel(lender.id,user.id)

            else:
                return {'message':'error_USER operation not allowed'}
            transaction.save_to_db()
            print("transaction_id:")
            print(transaction.Trx_id)
            lender.Trx_id = transaction.Trx_id
            user.Trx_id = transaction.Trx_id
            user.save_to_db()
            lender.save_to_db()

            return user.json()
        return {'error':'user does not exist'}

class repay(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('id',
                        type=int,
                        required=True,
                        help="ID(required) error "
                        )
    parser.add_argument('transaction',
                        type = int,
                        required = True,
                        help = "error: transaction id required for repayment"
                        )
    def post(self):
        data = repay.parser.parse_args()
        transaction = MappingModel.find_by_id(data['transaction'])

        if transaction and transaction.b_id == data['id']:
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
