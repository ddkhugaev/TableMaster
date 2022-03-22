import os

from flask import Flask
from flask import render_template
from data import db_session
from data.models import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


# Черновой вариант
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')


@app.route('/')
def index():
    return "Table Master"


def main():
    db_session.global_init("db/mars.db")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
