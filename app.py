import os
from flask import Flask
from flask_restful import Api

from resources.user import all_investment,InvestOperations,borrow,repay 

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'TEMP_TEST_XXXXX362357_SECRET_KEY'

api = Api(app)

@app.before_first_request
def create_tables():
    db.create_all()

api.add_resource(InvestOperations,'/invest')
api.add_resource(all_investment,'/all_investment')
api.add_resource(borrow,'/borrow')
api.add_resource(repay,'/repay')





if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True)
