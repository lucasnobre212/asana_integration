from sqlalchemy.ext.hybrid import hybrid_method

from . import db


class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.String(40), primary_key=True)
    refresh_token = db.Column(db.String(255), unique=True)
    access_token = db.Column(db.String(255), unique=True)
    expires_at = db.Column(db.Float)
    expires_in = db.Column(db.Integer)
    token_type = db.Column(db.String(16))

    @hybrid_method
    def get_token(self):
        token = self.__dict__
        token.pop('user_id', None)
        token.pop('_sa_instance_state', None)
        return token
