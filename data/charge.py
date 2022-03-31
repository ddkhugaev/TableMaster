import sqlalchemy
from .db_session import SqlAlchemyBase


class Charge(SqlAlchemyBase):
    __tablename__ = 'charge'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('user.id'))
    group_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('group.id'))
    subject = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    type = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    hours = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    requirements = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    preferences = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    semester = sqlalchemy.Column(sqlalchemy.String, nullable=True)
