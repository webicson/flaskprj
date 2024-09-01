from flask import render_template
from app import db
from app.errors import bp

@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404 # For these two errors, I'm returning the contents of their respective templates. Note that both functions return a second value after the template, which is the error code number. (the default is 200 (the status code for a successful response))

@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback() # To make sure any failed database sessions do not interfere with any database accesses triggered by the template, I issue a session rollback. This resets the session to a clean state.
    return render_template('errors/500.html'), 500