from db import db


class UserModel(db.Model):
    __tablename__ = 'users'

    Trx_id = db.Column(db.Integer,db.ForeignKey('mapping.Trx_id'))
    id = db.Column(db.Integer, primary_key=True)
    #username = db.Column(db.String(80))
    invest_amt = db.Column(db.Integer)
    #password = db.Column(db.String(80))
    lend_amt = db.Column(db.Integer)
    borrow_amt = db.Column(db.Integer)
    mappingModel = db.relationship('MappingModel')

    def __init__(self,invest_amt,lend_amt=0,borrow_amt=0):
        #self.username = username
        self.invest_amt = invest_amt
        self.lend_amt = lend_amt
        self.borrow_amt = borrow_amt
        #self.password = password

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def json(self):
        return {'id': self.id,
                'invest_amt': self.invest_amt,
                'lend_amt':self.lend_amt,
                'borrow_amt':self.borrow_amt}

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_investor(cls, borrow_request, _id):#more work needed
        all_investor = cls.query.all()
        for each_investor in all_investor:
            if each_investor.id != _id and each_investor.invest_amt > borrow_request:
                req_investor = each_investor
                break
        return req_investor
