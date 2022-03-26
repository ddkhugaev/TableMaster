import os

from flask import Flask, render_template
from data import db_session
from data.user import User
from data.charge import Charge
from data.fac import Fac
from data.group import Group
from data.audit import Audit
from data.lesson import Lesson

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


# Черновой вариант
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')


@app.route('/')
def index():
    return render_template('base.html')


def main():
    db_session.global_init("db/table.db")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
