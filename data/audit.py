import sqlalchemy
from .db_session import SqlAlchemyBase


class Audit(SqlAlchemyBase):
    __tablename__ = 'audit'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    number = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    feature = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    volume = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
