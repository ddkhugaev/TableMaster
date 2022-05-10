import os
from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_restful import Api
from data.forms import *
from data.api_resources import *
from data.user import User
from data.charge import Charge
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


API = Api(app)
API.add_resource(TimetableResource, '/api/timetable/<int:group_id>')
API.add_resource(GroupResource, '/api/group/<int:id>')
API.add_resource(GroupListResource, '/api/group')
API.add_resource(GroupGetter, '/api/get_group/<name>')


@lm.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html', title='Страница не найдена')


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html', title='Внутренняя ошибка сервера')


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
            login_user(user, remember=False)
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


@app.route('/', methods=['GET', 'POST'])
def index():
    form = IndexFilter()
    base = db_session.create_session()

    form.choice.choices = list(sorted([el.name for el in base.query(Group).all()]))
    if form.validate_on_submit():
        group_id = base.query(Group).filter(Group.name == form.choice.data).first().id
    else:
        group_id = int(flask.request.cookies.get("group", 1))
    group_name = base.query(Group).get(group_id).name
    form.choice.data = group_name

    charge = []
    audit = []
    involved = [el.id for el in base.query(Charge).filter(Charge.group_id == group_id).all()]
    for i in range(PAIRS_IN_A_DAY * 6):
        lesson = base.query(Lesson).filter(Lesson.charge_id.in_(involved),
                                           Lesson.weekday == i // PAIRS_IN_A_DAY,
                                           Lesson.pair_number == i % PAIRS_IN_A_DAY).first()
        if lesson:
            ch = base.query(Charge).get(lesson.charge_id)
            su = base.query(Subject).get(ch.subject_id)
            au = base.query(Audit).get(lesson.audit_id)
            te = base.query(Teacher).get(ch.teacher_id)
            charge.append(f'{su.title} ({te.surname} {te.name} {te.patronymic})')
            audit.append(f'Кабинет №{au.number}')
        else:
            charge.append('-')
            audit.append('-')

    res = flask.make_response(render_template('show_table.html', title='Добро пожаловать', charge=charge, audit=audit,
                                              form=form, pad=PAIRS_IN_A_DAY, week=WEEK, group=group_name))
    res.set_cookie("group", str(group_id), max_age=60 * 60 * 24 * 365 * 1)
    return res


@app.route('/timetable_list', methods=['GET', 'POST'])
def timetable_list():
    form = Search()
    base = db_session.create_session()
    groupids = set()
    for lesson in base.query(Lesson).all():
        ch = base.query(Charge).get(lesson.charge_id)
        groupids.add(ch.group_id)
    group = []
    for g in groupids:
        group.append((g, base.query(Group).get(g).name + ' (расписание)'))
    if form.validate_on_submit():
        for i in range(len(group) - 1, -1, -1):
            if form.search.data.lower() not in group[i][1].lower():
                del group[i]
    group.sort(key=lambda x: x[1])
    return render_template('timetable_list.html', title='Расписания', group=group, form=form)


@app.route('/group_choose', methods=['GET', 'POST'])
def group_choose():
    form = Search()
    base = db_session.create_session()
    group = [(el.id, f'(Курс {el.level}) {el.name}') for el in base.query(Group).all()]
    if form.validate_on_submit():
        for i in range(len(group) - 1, -1, -1):
            if form.search.data.lower() not in group[i][1].lower():
                del group[i]
    group.sort(key=lambda x: x[1])
    return render_template('group_choose.html', title='Выбор группы', group=group, form=form)


@app.route('/teacher_list', methods=['GET', 'POST'])
def teacher_list():
    form = Search()
    base = db_session.create_session()
    group = [(el.id, el.surname + ' ' + el.name + ' ' + el.patronymic) for el in base.query(Teacher).all()]
    if form.validate_on_submit():
        for i in range(len(group) - 1, -1, -1):
            if form.search.data.lower() not in group[i][1].lower():
                del group[i]
    group.sort(key=lambda x: x[1])
    return render_template('teacher_list.html', title='Учителя', group=group, form=form)


@app.route('/group_list', methods=['GET', 'POST'])
def group_list():
    form = Search()
    base = db_session.create_session()
    group = [(el.id, f'(Курс {el.level}) {el.name}') for el in base.query(Group).all()]
    if form.validate_on_submit():
        for i in range(len(group) - 1, -1, -1):
            if form.search.data.lower() not in group[i][1].lower():
                del group[i]
    group.sort(key=lambda x: x[1])
    return render_template('group_list.html', title='Группы', group=group, form=form)


@app.route('/charge_list', methods=['GET', 'POST'])
def charge_list():
    form = Search()
    base = db_session.create_session()
    group = []
    for el in base.query(Charge).all():
        te = base.query(Teacher).get(el.teacher_id)
        gr = base.query(Group).get(el.group_id)
        su = base.query(Subject).get(el.subject_id)
        group.append((el.id, f'{te.surname} {te.name} {te.patronymic}'
                             f'/{gr.name}/{su.title}({el.type}) '
                             f'({el.semester} семестр, {el.pairs} пар)'))
    if form.validate_on_submit():
        for i in range(len(group) - 1, -1, -1):
            if form.search.data.lower() not in group[i][1].lower():
                del group[i]
    group.sort(key=lambda x: x[1])
    return render_template('charge_list.html', title='Нагрузки', group=group, form=form)


@app.route('/subject_list', methods=['GET', 'POST'])
def subject_list():
    form = Search()
    base = db_session.create_session()
    group = [(el.id, el.title) for el in base.query(Subject).all()]
    if form.validate_on_submit():
        for i in range(len(group) - 1, -1, -1):
            if form.search.data.lower() not in group[i][1].lower():
                del group[i]
    group.sort(key=lambda x: x[1])
    return render_template('subject_list.html', title='Предметы', group=group, form=form)


@app.route('/audit_list', methods=['GET', 'POST'])
def audit_list():
    form = Search()
    base = db_session.create_session()
    group = [(el.id, f'Кабинет №{el.number} ({el.volume} чел.)') for el in base.query(Audit).all()]
    if form.validate_on_submit():
        for i in range(len(group) - 1, -1, -1):
            if form.search.data.lower() not in group[i][1].lower():
                del group[i]
    group.sort(key=lambda x: x[1])
    return render_template('audit_list.html', title='Аудитории', group=group, form=form)


@app.route('/teacher', methods=['GET', 'POST'])
@login_required
def add_teacher():
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
        return redirect('/teacher_list')
    return render_template('teacher.html', title='Добавление учителя', form=form)


@app.route('/teacher/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_teacher(id):
    form = TeacherForm()
    base = db_session.create_session()
    if flask.request.method == 'GET':
        load = base.query(Teacher).get(id)
        form.surname.data = load.surname
        form.name.data = load.name
        form.patronymic.data = load.patronymic
    if form.validate_on_submit():
        teacher = base.query(Teacher).get(id)
        teacher.surname = form.surname.data
        teacher.name = form.name.data
        teacher.patronymic = form.patronymic.data
        base.commit()
        return redirect('/teacher_list')
    return render_template('teacher.html', title='Изменение учителя', form=form)


@app.route('/group', methods=['GET', 'POST'])
@login_required
def add_group():
    form = GroupForm()
    if form.validate_on_submit():
        base = db_session.create_session()
        group = Group(
            name=form.name.data,
            level=form.level.data
        )
        base.add(group)
        base.commit()
        return redirect('/group_list')
    return render_template('group.html', title='Добавление группы', form=form)


@app.route('/group/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_group(id):
    form = GroupForm()
    base = db_session.create_session()
    if flask.request.method == 'GET':
        load = base.query(Group).get(id)
        form.name.data = load.name
        form.level.data = load.level
    if form.validate_on_submit():
        group = base.query(Group).get(id)
        group.name = form.name.data
        group.level = form.level.data
        base.commit()
        return redirect('/group_list')
    return render_template('group.html', title='Изменение группы', form=form)


@app.route('/charge', methods=['GET', 'POST'])
@login_required
def add_charge():
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
        return redirect('/charge_list')
    return render_template('charge.html', title='Добавление нагрузки', form=form)


@app.route('/charge/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_charge(id):
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
    if flask.request.method == 'GET':
        load = base.query(Charge).get(id)
        te = base.query(Teacher).get(load.teacher_id)
        gr = base.query(Group).get(load.group_id)
        su = base.query(Subject).get(load.subject_id)
        form.teacher_fio.data = f'{te.surname} {te.name} {te.patronymic}'
        form.group_name.data = gr.name
        form.subject_name.data = su.title
        form.type.data = load.type
        form.pairs.data = load.pairs
        form.semester.data = load.semester
    if form.validate_on_submit():
        f_i_o = form.teacher_fio.data.split()
        charge = base.query(Charge).get(id)
        charge.teacher_id = base.query(Teacher.id).filter(Teacher.surname == f_i_o[0],
                                                          Teacher.name == f_i_o[1],
                                                          Teacher.patronymic == f_i_o[2]
                                                         ).first()[0]
        charge.group_id = base.query(Group.id).filter(Group.name == form.group_name.data).first()[0]
        charge.subject_id = base.query(Subject.id).filter(Subject.title == form.subject_name.data).first()[0]
        charge.type = form.type.data
        charge.pairs = form.pairs.data
        charge.semester = form.semester.data
        base.commit()
        return redirect('/charge_list')
    return render_template('charge.html', title='Изменение нагрузки', form=form)


@app.route('/subject', methods=['GET', 'POST'])
@login_required
def add_subject():
    form = SubjectForm()
    if form.validate_on_submit():
        base = db_session.create_session()
        subject = Subject(
            title = form.title.data
        )
        base.add(subject)
        base.commit()
        return redirect('/subject_list')
    return render_template('subject.html', title='Добавление предмета', form=form)


@app.route('/subject/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_subject(id):
    form = SubjectForm()
    base = db_session.create_session()
    if flask.request.method == 'GET':
        load = base.query(Subject).get(id)
        form.title.data = load.title
    if form.validate_on_submit():
        subject = base.query(Subject).get(id)
        subject.title = form.title.data
        base.commit()
        return redirect('/subject_list')
    return render_template('subject.html', title='Изменение предмета', form=form)


@app.route('/audit', methods=['GET', 'POST'])
@login_required
def add_audit():
    form = AuditForm()
    if form.validate_on_submit():
        base = db_session.create_session()
        audit = Audit(
            number=form.number.data,
            volume=form.volume.data
        )
        base.add(audit)
        base.commit()
        return redirect('/audit_list')
    return render_template('audit.html', title='Добавление аудитории', form=form)


@app.route('/audit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_audit(id):
    form = AuditForm()
    base = db_session.create_session()
    if flask.request.method == 'GET':
        load = base.query(Audit).get(id)
        form.number.data = load.number
        form.volume.data = load.volume
    if form.validate_on_submit():
        audit = base.query(Audit).get(id)
        audit.number = form.number.data
        audit.volume = form.volume.data
        base.commit()
        return redirect('/audit_list')
    return render_template('audit.html', title='Изменение аудитории', form=form)


@app.route('/redactor/<int:group_id>', methods=['GET', 'POST'])
@login_required
def redactor(group_id):
    # <PAIRS_IN_A_DAY> полей на каждый день / вся неделя по порядку
    form = Redactor()
    base = db_session.create_session()
    chraw = base.query(Charge).filter(Charge.group_id == group_id)
    involved = [el.id for el in chraw]

    aud = list(map(lambda x: x[0], base.query(Audit.number).all()))
    ch = []
    for c in chraw:
        sj = base.query(Subject.title).filter(Subject.id == c.subject_id).first()[0]
        t = base.query(Teacher).filter(Teacher.id == c.teacher_id).first()
        ch.append(f'({c.pairs} пар) {sj} ({c.type})'
                  f' ({t.surname + " " + t.name + " " + t.patronymic})'
                  f' | {c.id}')

    for i in range(PAIRS_IN_A_DAY * 6):
        ch_f = ch[::]
        aud_f = aud[::]
        for lesson in base.query(Lesson).filter(Lesson.charge_id.notin_(involved),
                                                Lesson.weekday == i // PAIRS_IN_A_DAY,
                                                Lesson.pair_number == i % PAIRS_IN_A_DAY):
            teacher = base.query(Teacher).filter(
                Teacher.id == base.query(Charge).filter(Charge.id == lesson.charge_id).first().teacher_id
            ).first()
            t_name = f'{teacher.surname} {teacher.name} {teacher.patronymic}'
            for j in range(len(ch_f)):
                if t_name in ch_f[j]:
                    del ch_f[j]
                    break
            try:
                del aud_f[aud_f.index(base.query(Audit).filter(Audit.id == lesson.audit_id).first().number)]
            except Exception:
                pass
        form.charges[i].choices = ['<выбрать нагрузку>'] + ch_f
        form.audits[i].choices = ['<выбрать аудиторию>'] + aud_f

    if flask.request.method == 'GET':
        for lesson in base.query(Lesson).filter(Lesson.charge_id.in_(involved)).all():
            form.charges[lesson.weekday * PAIRS_IN_A_DAY + lesson.pair_number].data = \
                [c for c in ch if c.split(' | ')[-1] == str(lesson.charge_id)][0]
            form.audits[lesson.weekday * PAIRS_IN_A_DAY + lesson.pair_number].data = \
                str(base.query(Audit).filter(Audit.id == lesson.audit_id).first().number)

    if form.validate_on_submit():
        usage_counter = {}
        for i in range(PAIRS_IN_A_DAY * 6):
            clear = form.charges[i].data == '<выбрать нагрузку>' or form.audits[i].data == '<выбрать аудиторию>'
            lesson = base.query(Lesson).filter(Lesson.charge_id.in_(involved),
                                               Lesson.weekday == i // PAIRS_IN_A_DAY,
                                               Lesson.pair_number == i % PAIRS_IN_A_DAY).first()
            if lesson:
                if clear:
                    base.delete(lesson)
                    continue
                lesson.charge_id = int(form.charges[i].data.split(' | ')[-1])
                lesson.audit_id = base.query(Audit).filter(Audit.number == form.audits[i].data).first().id
            else:
                if clear:
                    continue
                lesson = Lesson()
                lesson.charge_id = int(form.charges[i].data.split(' | ')[-1])
                lesson.audit_id = base.query(Audit).filter(Audit.number == form.audits[i].data).first().id
                lesson.weekday = i // PAIRS_IN_A_DAY
                lesson.pair_number = i % PAIRS_IN_A_DAY
                base.add(lesson)
            if lesson.charge_id not in usage_counter:
                usage_counter[lesson.charge_id] = 0
            usage_counter[lesson.charge_id] += 1

        errors = []
        for k in usage_counter:
            el = base.query(Charge).get(k)
            te = base.query(Teacher).get(el.teacher_id)
            gr = base.query(Group).get(el.group_id)
            su = base.query(Subject).get(el.subject_id)
            if el.pairs > usage_counter[k]:
                errors.append(f'Нагрузка {te.surname} {te.name} {te.patronymic}/{gr.name}/{su.title}({el.type}) '
                              f'({el.semester} семестр) используется реже, чем {el.pairs} раз(-а)')
            elif el.pairs < usage_counter[k]:
                errors.append(f'Нагрузка {te.surname} {te.name} {te.patronymic}/{gr.name}/{su.title}({el.type}) '
                              f'({el.semester} семестр) используется чаще, чем {el.pairs} раз(-а)')
        if errors:
            base.rollback()
            return render_template('table_redactor.html', title='Создание расписания', form=form,
                                   pad=PAIRS_IN_A_DAY, week=WEEK, group=base.query(Group).get(group_id).name,
                                   msg=errors)
        base.commit()
        return redirect('/timetable_list')

    return render_template('table_redactor.html', title='Создание расписания', form=form,
                           pad=PAIRS_IN_A_DAY, week=WEEK, group=base.query(Group).get(group_id).name)


@app.route('/delete/<subject>/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(subject, id):
    form = OKForm()
    base = db_session.create_session()
    if subject == 'teacher':
        obj = base.query(Teacher).get(id)
        name = '(Учитель) ' + obj.surname + ' ' + obj.name + ' ' + obj.patronymic
        conflicts = [base.query(Charge).filter(Charge.teacher_id == id).all()]
    elif subject == 'group':
        obj = base.query(Group).get(id)
        name = '(Группа) ' + f'(Курс {obj.level}) {obj.name}'
        conflicts = [base.query(Charge).filter(Charge.group_id == id).all()]
    elif subject == 'charge':
        obj = base.query(Charge).get(id)
        te = base.query(Teacher).get(obj.teacher_id)
        gr = base.query(Group).get(obj.group_id)
        su = base.query(Subject).get(obj.subject_id)
        name = f'(Нагрузка) {te.surname} {te.name} {te.patronymic}'
        f'/{gr.name}/{su.title}({obj.type}) '
        f'({obj.semester} семестр, {obj.pairs} пар)'
        conflicts = [base.query(Lesson).filter(Lesson.charge_id == id).all()]
    elif subject == 'subject':
        obj = base.query(Subject).get(id)
        name = '(Предмет) ' + obj.title
        conflicts = [base.query(Charge).filter(Charge.subject_id == id).all()]
    elif subject == 'audit':
        obj = base.query(Audit).get(id)
        name = 'Кабинет №' + str(obj.number) + f'({obj.volume} чел.)'
        conflicts = [base.query(Lesson).filter(Lesson.audit_id == id).all()]

    if form.validate_on_submit():
        base.delete(obj)
        base.commit()
        return redirect(f'/{subject}_list')
    
    if any(conflicts):
        return render_template('9403.html', name=name, bacc=f'/{subject}_list', title='Удаление')
        
    return render_template('are_you_sure.html', title='Потверждение удаления', name=name, form=form)


@app.route('/timetable_discard/<int:group_id>', methods=['GET', 'POST'])
def delete_timetable(group_id):
    form = OKForm()
    if flask.request.method == 'GET':
        form.confirm.data = False
    base = db_session.create_session()
    name = base.query(Group).get(group_id).name

    if form.validate_on_submit():
        involved = [el.id for el in base.query(Charge).filter(Charge.group_id == group_id).all()]
        for lesson in base.query(Lesson).filter(Lesson.charge_id.in_(involved)):
            base.delete(lesson)
        base.commit()
        return redirect('/timetable_list')

    return render_template('are_you_sure.html', title='Потверждение удаления', name=f'Расписание для {name}', form=form)


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
