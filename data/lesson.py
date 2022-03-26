import sqlalchemy
from .db_session import SqlAlchemyBase


class Lesson(SqlAlchemyBase):
    __tablename__ = 'lesson'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    charge_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('charge.id'))
    group_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('group.id'))
    audit_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('audit.id'))
    couple_number = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
