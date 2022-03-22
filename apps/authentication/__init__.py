# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import Blueprint
app = Flask(__name__)
blueprint = Blueprint(
    'authentication_blueprint',
    __name__,
    url_prefix=''
)

app.config['SECRET_KEY'] = "JLKJJJO3IURYoiouolnojojouuoo=5y9y9youjuy952oohhbafdnoglhoho"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenseDB.db'

db = SQLAlchemy(app)

from apps.authentication import routes