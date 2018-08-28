from db import db


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80),unique=True)
    password = db.Column(db.String(80))

    invest_amt = db.Column(db.Integer)
    lend_amt = db.Column(db.Integer)
    borrow_amt = db.Column(db.Integer)

    Trx_id = db.Column(db.Integer,db.ForeignKey('mapping.Trx_id'))
    weight_id = db.Column(db.Integer)

    mappingModel = db.relationship('MappingModel')
    investRequestModel = db.relationship('InvestRequestModel')
    withdrawRequestModel = db.relationship('WithdrawRequestModel')
    BorrowRequestModel = db.relationship('BorrowRequestModel')

    def __init__(self,username,password,invest_amt=0,lend_amt=0,borrow_amt=0,weight_id=0):
        self.username = username
        self.password = password
        self.invest_amt = invest_amt
        self.lend_amt = lend_amt
        self.borrow_amt = borrow_amt
        self.weight_id = weight_id


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def json(self):
        return {'id':self.id,
                'username':self.username,
                'invest_amt':self.invest_amt,
                'lend_amt':self.lend_amt,
                'borrow_amt':self.borrow_amt,
                'transaction':self.Trx_id,
                'weight_id':self.weight_id}

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_investor(cls, borrow_request, username):#more work needed
        req_investor = None
        all_investor = cls.query.order_by(cls.weight_id).all()
        for each_investor in all_investor:
            if each_investor.username != username and each_investor.invest_amt > borrow_request:
                req_investor = each_investor
                break
        return req_investor

    @classmethod
    def find_all(cls):
        return cls.query.all()
