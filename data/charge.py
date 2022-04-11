import sqlalchemy
from .db_session import SqlAlchemyBase


class Charge(SqlAlchemyBase):
    __tablename__ = 'charge'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    teacher_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('teacher.id'))
    group_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('group.id'))
    subject_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('subject.id'))
    type = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    pairs = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    semester = sqlalchemy.Column(sqlalchemy.String, nullable=True)
