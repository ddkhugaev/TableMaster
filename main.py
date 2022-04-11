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

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
lm = LoginManager()
lm.init_app(app)


@lm.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


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


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')


@app.route('/')
def index():
    return render_template('base.html')


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
