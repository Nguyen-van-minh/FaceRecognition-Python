# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""


from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField, StringField, SelectField, SubmitField, IntegerField
from wtforms.validators import Email, DataRequired
# login and registration


class LoginForm(FlaskForm):
    username = TextField('Username',
                         id='username_login',
                         validators=[DataRequired()])
    password = PasswordField('Password',
                             id='pwd_login',
                             validators=[DataRequired()])


class CreateAccountForm(FlaskForm):
    username = TextField('Username',
                         id='username_create',
                         validators=[DataRequired()])
    email = TextField('Email',
                      id='email_create',
                      validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             id='pwd_create',
                             validators=[DataRequired()])


class UserDataForm(FlaskForm):
    type = SelectField('Type', validators=[DataRequired()],
                       choices=[('income', 'income'),
                                ('expense', 'expense')])
    category = SelectField("Category", validators=[DataRequired()],
                           choices=[('rent', 'rent'),
                                    ('salary', 'salary'),
                                    ('investment', 'investment'),
                                    ('Save', 'Save')
                                    ]
                           )
    amount = IntegerField('Amount', validators=[DataRequired()])
    submit = SubmitField('Add Report')
