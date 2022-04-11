from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, SubmitField,\
    BooleanField, SelectField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Электронная почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()],
                             description='Придумайте и запишите сложный пароль')
    pwcheck = PasswordField('Повторите пароль', validators=[DataRequired()])
    invite = PasswordField('Код регистрации', validators=[DataRequired()],
                           description='Код можно получить у администратора')
    submit = SubmitField('Зарегистрироваться')

class LoginForm(FlaskForm):
    email = EmailField('Электронная почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class InviteForm(FlaskForm):
    full_name = StringField('ФИО пользователя')
    role = SelectField('Роль', choices=['Учитель', 'Администратор'],
                       validators=[DataRequired()])
    code = StringField('Код регистрации', description='Придумайте и запишите трудноподбираемый код',
                       validators=[DataRequired()])
    submit = SubmitField('Пригласить')