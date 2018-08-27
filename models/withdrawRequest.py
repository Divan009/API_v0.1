from db import db

class WithdrawRequestModel(db.Model):
    __tablename__ = "withdrawRequest"

    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),unique=True)
    amount = db.Column(db.Integer)
    order_id = db.Column(db.String(80))
    success = db.Column(db.Integer)

    requestModel = db.relationship('UserModel')


    def __init__(self,user_id,amount,order_id,success):
        self.user_id = user_id
        self.amount = amount
        self.order_id = order_id
        self.success = success

    def json(self):
        return {'id':self.id,
                'user_id':self.user_id,
                'amount':self.amount,
                'order_id':self.order_id,
                'success':self.success}

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_Userid(cls, user_id):
        return cls.query.filter_by(user_id=user_id).first()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_all(cls):
        return cls.query.all()
