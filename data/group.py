import sqlalchemy
from .db_session import SqlAlchemyBase


class Group(SqlAlchemyBase):
    __tablename__ = 'group'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    fac_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('fac.id'))
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    level = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
