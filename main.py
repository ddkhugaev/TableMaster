import os

from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, logout_user, login_required
from data import db_session
from data.forms import *
from data.user import User
from data.charge import Charge
from data.fac import Fac
from data.group import Group
from data.audit import Audit
from data.lesson import Lesson
from data.teacher import Teacher
from data.subject import Subject


WEEK = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
lm = LoginManager()
lm.init_app(app)


@lm.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.pwcheck.data:
            return render_template('register.html', title='Регистрация',
                                   form=form, msg='Пароли не совпадают')
        base = db_session.create_session()
        if base.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form, msg='Почта уже занята')
        if base.query(User).filter(User.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form, msg='Имя уже используется')
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        base.add(user)
        base.commit()
        login_user(user)
        return redirect('/')
    return render_template('register.html', title='Регистрация',
                           form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if not user:
            user = db_sess.query(User).filter(User.name == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', title='Авторизация',
                               msg="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/')
def index():
    return render_template('base.html')


@app.route('/teacher', methods=['GET', 'POST'])
def teacher():
    form = TeacherForm()
    if form.validate_on_submit():
        base = db_session.create_session()
        teacher = Teacher(
            surname=form.surname.data,
            name=form.name.data,
            patronymic=form.patronymic.data
        )
        base.add(teacher)
        base.commit()
        return redirect('/')
    return render_template('teacher.html', title='Добавление учителя', form=form)


@app.route('/group', methods=['GET', 'POST'])
def group():
    form = GroupForm()
    if form.validate_on_submit():
        base = db_session.create_session()
        group = Group(
            name=form.name.data,
            level=form.level.data
        )
        base.add(group)
        base.commit()
        return redirect('/')
    return render_template('group.html', title='Добавление группы', form=form)


@app.route('/charge', methods=['GET', 'POST'])
def charge():
    base = db_session.create_session()
    form = ChargeForm()
    form.teacher_fio.choices = list(map(lambda x: ' '.join(x),
                                        base.query(
        Teacher.surname,
        Teacher.name,
        Teacher.patronymic
    ).all()))
    form.group_name.choices = list(map(lambda x: x[0],
                               base.query(Group.name).all()))
    form.subject_name.choices = list(map(lambda x: x[0],
                                 base.query(Subject.title).all()))

    if form.validate_on_submit():
        f_i_o = form.teacher_fio.data.split()
        charge = Charge(
            teacher_id = base.query(Teacher.id).filter(Teacher.surname == f_i_o[0],
                                                       Teacher.name == f_i_o[1],
                                                       Teacher.patronymic == f_i_o[2]
                                                       ).first()[0],
            group_id = base.query(Group.id).filter(Group.name == form.group_name.data
                                                   ).first()[0],
            subject_id = base.query(Subject.id).filter(Subject.title == form.subject_name.data
                                                       ).first()[0],
            type=form.type.data,
            pairs=form.pairs.data,
            semester=form.semester.data
        )
        base.add(charge)
        base.commit()
        return redirect('/')
    return render_template('charge.html', title='Добавление нагрузки', form=form)


@app.route('/subject', methods=['GET', 'POST'])
def subject():
    form = SubjectForm()
    if form.validate_on_submit():
        base = db_session.create_session()
        subject = Subject(
            title = form.title.data
        )
        base.add(subject)
        base.commit()
        return redirect('/')
    return render_template('subject.html', title='Добавление предмета', form=form)


@app.route('/audit', methods=['GET', 'POST'])
def audit():
    form = AuditForm()
    if form.validate_on_submit():
        base = db_session.create_session()
        audit = Audit(
            number=form.number.data,
            volume=form.volume.data
        )
        base.add(audit)
        base.commit()
        return redirect('/')
    return render_template('audit.html', title='Добавление учителя', form=form)


@app.route('/redactor')
def redactor():
    # <PAIRS_IN_A_DAY> полей на каждый день / вся неделя по порядку
    form = Redactor()
    db = db_session.create_session()
    chraw = db.query(Charge).all()
    aud = ['<выбрать кабинет>'] + list(map(lambda x: x[0], db.query(Audit.number).all()))
    print(aud)
    ch = ['<выбрать нагрузку>']
    for c in chraw:
        sj = db.query(Subject.title).filter(Subject.id == c.subject_id).first()[0]
        t = db.query(Teacher).filter(Teacher.id == c.teacher_id).first()
        ch.append(f'{sj} ({c.type})'
                      f' ({t.surname + " " + t.name + " " + t.patronymic})'
                      f' | {c.id}')
    for field in form.charges:
        field.choices = ch
    for field in form.audits:
        field.choices = aud
    print(form._fields.keys())
    return render_template('table_redactor.html', title='Создание расписания', form=form,
                           pad=PAIRS_IN_A_DAY, week=WEEK, group='< вставить название группы >')


def main():
    db_session.global_init("db/table.db")

    # base = db_session.create_session()    # asdasdasd
    #
    # user = User(
    #     name='a',
    #     email='a@a.a'
    # )
    # user.set_password('1')
    # base.add(user)
    #
    # base.commit()

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
