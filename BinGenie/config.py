import os

class Config(object):
    # General Config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secure-key'
    DEBUG = False
    TESTING = False
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = f'postgresql://{os.environ.get("DATABASE_USER")}:{os.environ.get("DATABASE_PASSWORD")}@localhost/bin_genie_database'

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://nathan:Robert19940@localhost/bine_genie_database'

class TestingConfig(Config):
    TESTING = True
