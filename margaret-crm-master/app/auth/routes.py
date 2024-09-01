from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_babel import _
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from app.auth.email import send_password_reset_email


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: # is_authenticated: a property that is True if the user has valid credentials or False otherwise.
        return redirect(url_for('main.index')) # Flask provides a function called url_for(), which generates URLs using its internal mapping of URLs to view functions
    # The top two lines in the login() function deal with a weird situation. Imagine you have a user that is logged in, and the user navigates to the /login URL of your application. Clearly that is a mistake, so I want to not allow that.
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first() #The username came with the form submission, so I can query the database with that to find the user. For this purpose I'm using the filter_by() method of the SQLAlchemy query object. The result of filter_by() is a query that only includes the objects that have a matching username. Since I know there is only going to be one or zero results, I complete the query by calling first(), which will return the user object if it exists, or None if it does not.
        if user is None or not user.check_password(form.password.data): #If I got a match for the username that was provided, I can next check if the password that also came with the form is valid.
            flash('Invalid username or password')
            return redirect(url_for('auth.login')) # redirect back to the login prompt so that the user can try again.
        login_user(user, remember=form.remember_me.data) # If the username and password are both correct, then I call the login_user() function, which comes from Flask-Login. This function will register the user as logged in, so that means that any future pages the user navigates to will have the current_user variable set to that user.
                                                            #  redirect back from the successful login to the page the user wanted to access.
        next_page = request.args.get('next') #  the value of the next query string argument is obtained. Flask provides a request variable that contains all the information that the client sent with the request
        if not next_page or url_parse(next_page).netloc != '': # To determine if the URL is relative or absolute, I parse it with Werkzeug's url_parse() function and then check if the netloc component is set or not.
            next_page = url_for('main.index')  #  redirect the newly logged-in user to the index page
        return redirect(next_page)
    return render_template('auth/login.html', title=_('Sign In'), form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: # make sure the user that invokes this route is not logged in.
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email = form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title=_('Register'), form=form)

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user) # send a password reset email. I'm using a send_password_reset_email() helper function to do this.
        flash(_('Check your email for the instructions to reset your password'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', title=_('Reset Password'), form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated: # make sure the user is not logged in,
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token) #  I determine who the user is by invoking the token verification method in the User class. This method returns the user if the token is valid, or None if not.
    if not user: # If the token is invalid I redirect to the home page.
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit(): # If the token is valid, then I present the user with a second form, in which the new password is requested.
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)