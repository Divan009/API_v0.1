from db import db

class WithdrawRequestModel(db.Model):
    __tablename__ = "withdrawRequest"

    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    amount = db.Column(db.Integer)

    requestModel = db.relationship('UserModel')


    def __init__(self,user_id,amount):
        self.user_id = user_id
        self.amount = amount

    def json(self):
        return {'id':self.id,
                'user_id':self.user_id,
                'amount':self.amount}

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_all(cls):
        return cls.query.all()
