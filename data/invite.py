import sqlalchemy
from .db_session import SqlAlchemyBase


class Invite(SqlAlchemyBase):
    __tablename__ = 'invite'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    full_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    role = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    code = sqlalchemy.Column(sqlalchemy.String, nullable=True)