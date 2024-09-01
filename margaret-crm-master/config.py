import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    #mysql+pymysql://root:@localhost:3306/microblog

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # email server details:
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['naama@israelnumber.com']
    POSTS_PER_PAGE = 6
    LANGUAGES = ['en', 'es', 'he']
    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
    RIVHIT_API_TOKEN = 'decd03e5-e35c-41e8-84f7-fba2fb483928'
    NEXMO_API_KEY = '8c3b2c58'
    NEXMO_API_SECRET = 'zAV1gd8jJ5KtmbdU'
    # RIVHIT_API_TOKEN = 'decd03e5-e35c-41e8-84f7-fba2fb483928111'
    APP_NAME = 'Margaret'

