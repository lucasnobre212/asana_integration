from sqlalchemy.dialects.postgresql import JSONB

from . import db


class Credential(db.Model):
    __tablename__ = 'import_credentials'
    userId = db.Column(db.String(63), primary_key=True)
    companyId = db.Column(db.String(255), primary_key=True)
    credentials = db.Column(JSONB)
