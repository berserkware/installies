import bleach

from flask import Blueprint, render_template, redirect, abort, request, g, flash
from installies.lib.validate import ValidationError
from installies.blueprints.auth.validate import (
    PasswordValidator,
    UsernameValidator,
    EmailValidator,
    PasswordConfirmValidator,
)
from installies.blueprints.auth.models import User
from installies.blueprints.auth.decorators import (
    unauthenticated_required,
    authenticated_required,
)
from peewee import *
from datetime import date
import calendar

auth = Blueprint('auth', __name__)


@auth.route('/signup', methods=['GET', 'POST'])
@unauthenticated_required()
def signup():
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
        except ValidationError as e:
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
@unauthenticated_required()
def login():
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
        
        # if a referer is sent in the params, redirect to there instead
        referer = request.args.get('referer')
        if referer is not None:
            referer = bleach.clean(referer)
            res = redirect(referer)
        
        res.set_cookie('user-token', user.token)
        flash('You are now logged in.', 'success')
        return res
    else:
        return render_template('login.html')


@auth.route('/logout', methods=['GET', 'POST'])
@authenticated_required()
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

    return render_template(
        'profile.html',
        user=user
    )
