import flask
from flask_restful import Resource, abort
from data.user import User
from data.charge import Charge
from data.group import Group
from data.audit import Audit
from data.lesson import Lesson
from data.teacher import Teacher
from data.subject import Subject
from data import db_session
from data.forms import PAIRS_IN_A_DAY as PAD


WEEK = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']


class TimetableResource(Resource):
    def get(self, group_id):
        base = db_session.create_session()
        group = base.query(Group).get(group_id)
        if not group:
            abort(404, message=f'Group with ID "{group_id}" not found')
        involved = [el.id for el in base.query(Charge).filter(Charge.group_id == group_id).all()]

        subject = []
        teacher = []
        audit = []
        for i in range(PAD * 6):
            lesson = base.query(Lesson).filter(Lesson.charge_id.in_(involved),
                                               Lesson.weekday == i // PAD,
                                               Lesson.pair_number == i % PAD).first()
            if lesson:
                ch = base.query(Charge).get(lesson.charge_id)
                su = base.query(Subject).get(ch.subject_id)
                au = base.query(Audit).get(lesson.audit_id)
                te = base.query(Teacher).get(ch.teacher_id)
                subject.append(su.title)
                teacher.append(f'{te.surname} {te.name} {te.patronymic}')
                audit.append(au.number)
            else:
                subject.append(None)
                teacher.append(None)
                audit.append(None)
        res = {
            'group': base.query(Group).get(group_id).name,
            'timetable': {
                WEEK[i]: [
                    {
                        'subject': subject[i * PAD + j],
                        'teacher': teacher[i * PAD + j],
                        'auditory': audit[i * PAD + j]
                    } for j in range(PAD)
                ] for i in range(6)
            }
        }
        return flask.jsonify(res)


class GroupListResource(Resource):
    def get(self):
        base = db_session.create_session()
        groups = base.query(Group).all()
        res = [
            {
                'level': el.level,
                'name': el.name
            } for el in groups
        ]
        return flask.jsonify(res)


class GroupResource(Resource):
    def get(self, id):
        base = db_session.create_session()
        group = base.query(Group).get(id)
        if not group:
            abort(404, message=f'Group with ID "{id}" not found')
        res = {
            'level': group.level,
            'name': group.name
        }
        return flask.jsonify(res)


class GroupGetter(Resource):
    def get(self, name):
        base = db_session.create_session()
        groups = base.query(Group).filter(Group.name.like(f'%{name}%')).all()
        res = [
            {
                'id': g.id,
                'level': g.level,
                'name': g.name
            } for g in groups
        ]
        return flask.jsonify(res)