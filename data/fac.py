import sqlalchemy
from .db_session import SqlAlchemyBase


class Fac(SqlAlchemyBase):
    __tablename__ = 'fac'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    dean_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('user.id'))
