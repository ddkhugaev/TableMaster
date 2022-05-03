from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, SubmitField, \
    BooleanField, IntegerField, SelectField, FieldList
from wtforms.validators import DataRequired


PAIRS_IN_A_DAY = 4


class RegisterForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    email = EmailField('Электронная почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    pwcheck = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    email = StringField('Электронная почта или имя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class TeacherForm(FlaskForm):
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    patronymic = StringField('Отчество', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class GroupForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    level = IntegerField('Номер курса', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class ChargeForm(FlaskForm):
    teacher_fio = SelectField('Учитель', validators=[DataRequired()])
    group_name = SelectField('Группа', validators=[DataRequired()])
    subject_name = SelectField('Предмет', validators=[DataRequired()])
    type = SelectField('Тип', choices=['Лекции', 'Практика', 'Лабораторные'],
                       validators=[DataRequired()])
    semester = StringField('Семестр', validators=[DataRequired()])
    pairs = IntegerField('Количество пар', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class SubjectForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class AuditForm(FlaskForm):
    number = IntegerField('Номер', validators=[DataRequired()])
    volume = IntegerField('Вместимость', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class Redactor(FlaskForm):
    charges = FieldList(SelectField(), min_entries=PAIRS_IN_A_DAY * 6)
    audits = FieldList(SelectField(), min_entries=PAIRS_IN_A_DAY * 6)
    submit = SubmitField('Сохранить и проверить')

class OKForm(FlaskForm):
    confirm = BooleanField('Я нахожусь в добром здравии и хочу продолжить', default=True, validators=[DataRequired()])
    submit = SubmitField('Подтвердить')