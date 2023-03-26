import bleach

from flask import Blueprint, render_template, redirect, abort, request, g, flash
from installies.apps.auth.validate import (
    PasswordValidator,
    UsernameValidator,
    EmailValidator,
    PasswordConfirmValidator,
)
from installies.apps.auth.models import User
from peewee import *
from datetime import date
import calendar

auth = Blueprint('auth', __name__)


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    # Checks if user is authenticated
    if g.is_authed:
        return redirect('/')

    if request.method == 'POST':
        # Gets the form data
        username = request.form.get('username').strip()
        email = request.form.get('email').strip()
        password = request.form.get('password').strip()
        password_confirm = request.form.get('password-confirm').strip()

        try:
            UsernameValidator.validate(username)
            EmailValidator.validate(email)
            PasswordValidator.validate(password)
            PasswordConfirmValidator.validate(password_confirm)
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('signup.html')

        # Checks if passwords match
        if password != password_confirm:
            flash('Passwords do not match.', 'error')
            return render_template('signup.html')

        username = bleach.clean(username)

        new_user = User.create(username, email, password)

        # If success, return response with cookie
        res = redirect('/')
        res.set_cookie('user-token', new_user.token)
        flash('Account successfully created.')
        return res
    else:
        return render_template('signup.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Checks that user is authenticated
    if g.is_authed:
        return redirect('/')

    if request.method == 'POST':
        # Gets the POST data
        username = request.form.get('username')
        password = request.form.get('password')

        # Checks that all correct POST data is present
        if username is None:
            flash('You need to supply a username.', 'error')
            return render_template('login.html')
        if password is None:
            flash('You need to supply a password.', 'error')
            return render_template('login.html')

        user = User.select().where(User.username == username)

        if user.exists() is False:
            flash('Could not find a user with that username.', 'error')
            return render_template('login.html')

        user = user.get()

        # Checks password is correct
        if user.match_password(password) is False:
            flash('Password is incorrect.', 'error')
            return render_template('login.html')

        res = redirect('/')
        res.set_cookie('user-token', user.token)
        flash('You are now logged in.', 'success')
        return res
    else:
        return render_template('login.html')


@auth.route('/logout', methods=['GET', 'POST'])
def logout():
    res = redirect('/')
    res.set_cookie('user-token', 'deleted', '/', '-1')
    flash('You are now logged out.', 'success')
    return res


@auth.route('/profile/<username>')
def profile(username):
    user = User.select().where(User.username == username)
    
    if user.exists() is False:
        abort(404)

    user = user.get()

    username = bleach.clean(user.username)

    return render_template(
        'profile.html',
        **{
            'username': username,
            'is_admin': user.admin,
            'day_joined': user.creation_date.day,
            'month_joined': calendar.month_name[user.creation_date.month],
            'year_joined': user.creation_date.year,
        }
    )
