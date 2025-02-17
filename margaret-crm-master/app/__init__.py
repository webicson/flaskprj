import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l
from config import Config
from elasticsearch import Elasticsearch

app = Flask(__name__)
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _l('Please log in to access this page.')
mail = Mail(app)
bootstrap = Bootstrap()
moment = Moment()
babel = Babel()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.customers import bp as customers_bp
    app.register_blueprint(customers_bp, url_prefix='/customers')

    from app.dids import bp as dids_bp
    app.register_blueprint(dids_bp, url_prefix='/dids')

    from app.vendors import bp as vendors_bp
    app.register_blueprint(vendors_bp, url_prefix='/vendors')

    from app.mange import bp as mange_bp
    app.register_blueprint(mange_bp, url_prefix='/mange')

    from app.sms import bp as sms_bp
    app.register_blueprint(sms_bp, url_prefix='/sms' )

    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None

    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'],
                        app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Margaret Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/microblog.log',
                                           maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Margaret startup')

    return app


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])


from app import models

# import logging
# from logging.handlers import SMTPHandler, RotatingFileHandler
# import os
# from flask import Flask, request, current_app
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
# from flask_login import LoginManager
# from flask_mail import Mail
# from flask_bootstrap import Bootstrap
# from flask_moment import Moment
# from flask_babel import Babel, lazy_gettext as _l
# from config import Config
#
#
# db = SQLAlchemy()
# migrate = Migrate()
# login = LoginManager()
# login.login_view = 'auth.login' # The 'login' value above is the function (or endpoint) name for the login view. In other words, the name you would use in a url_for() call to get the URL.
# login.login_message = _l('Please log in to access this page.')
# mail = Mail()
# bootstrap = Bootstrap()
# moment = Moment()
# babel = Babel()
#
# # app = Flask(__name__)
# # app.config.from_object(Config)
# # db = SQLAlchemy(app)
# # migrate = Migrate(app, db)
# # login = LoginManager(app)
# # login.login_view = 'login'
# # login.login_message = _l('Please log in to access this page.')
# # mail = Mail(app)
# # bootstrap = Bootstrap(app)
# # moment = Moment(app)
# # babel = Babel(app)
#
#
# def create_app(config_class=Config):
#     app = Flask(__name__)
#     app.config.from_object(config_class)
#
#     db.init_app(app)
#     migrate.init_app(app, db)
#     login.init_app(app)
#     mail.init_app(app)
#     bootstrap.init_app(app)
#     moment.init_app(app)
#     babel.init_app(app)
#
# # blueprint registration
#     from app.errors import bp as errors_bp
#     app.register_blueprint(errors_bp)
#
#     from app.auth import bp as auth_bp
#     app.register_blueprint(auth_bp, url_prefix='/auth')
#
#     from app.main import bp as main_bp
#     app.register_blueprint(main_bp)
#
# # logging setup
#     if not app.debug: # Im only going to enable the email logger when the application is running without debug mode, which is indicated by app.debug being True
#         if app.config['MAIL_SERVER']: #And also when the email server exists in the configuration.
#             auth = None
#             if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
#                 auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
#             secure = None
#             if app.config['MAIL_USE_TLS']:
#                 secure = ()
#             mail_handler = SMTPHandler(
#                 mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
#                 fromaddr='no-reply@' + app.config['MAIL_SERVER'],
#                 toaddrs=app.config['ADMINS'], subject='Margaret Failure',
#                 credentials=auth, secure=secure)
#             mail_handler.setLevel(logging.ERROR)
#             app.logger.addHandler(mail_handler)
#
#         if not os.path.exists('logs'):
#             os.mkdir('logs')
#         file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10) # The RotatingFileHandler class is nice because it rotates the logs, ensuring that the log files do not grow too large when the application runs for a long time. In this case I'm limiting the size of the log file to 10KB, and I'm keeping the last ten log files as backup.
#         file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')) # The logging.Formatter class provides custom formatting for the log messages. Since these messages are going to a file, I want them to have as much information as possible. So I'm using a format that includes the timestamp, the logging level, the message and the source file and line number from where the log entry originated.
#         file_handler.setLevel(logging.INFO) #To make the logging more useful, I'm also lowering the logging level to the INFO category, both in the application logger and the file logger handler.
#         app.logger.addHandler(file_handler)
#
#         app.logger.setLevel(logging.INFO)
#         app.logger.info('Margaret startup')
#
#     return app
#
# @babel.localeselector
# def get_locale():
#     return request.accept_languages.best_match(app.config['LANGUAGES']) # Here I'm using an attribute of Flask's request object called accept_languages. This object provides a high-level interface to work with the Accept-Language header that clients send with a request. This header specifies the client language and locale preferences as a weighted list. The contents of this header can be configured in the browser's preferences page, with the default being usually imported from the language settings in the computer's operating system
#     # return 'he'
#
# from app import models
# # from app.auth import routes