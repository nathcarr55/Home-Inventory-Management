import os

class Config(object):
    # General Config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secure-key'
    DEBUG = False
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://nathan:Robert19940@localhost/bine_genie_database'

class TestingConfig(Config):
    TESTING = True
