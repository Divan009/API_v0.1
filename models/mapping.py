from db import db

class MappingModel(db.Model):
    __tablename__ = 'mapping'

    Trx_id = db.Column(db.Integer,primary_key=True)
    l_id = db.Column(db.Integer)
    b_id = db.Column(db.Integer)

    userModel = db.relationship('UserModel')

    def __init__(self,l_id,b_id):
        self.l_id = l_id
        self.b_id = b_id

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(Trx_id=_id).first()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_all(cls):
        return cls.query.all()
