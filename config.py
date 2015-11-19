import os
# get the absolute path of config.py
basedir = os.path.abspath(os.path.dirname(__file__))
upload_dir = os.path.join(basedir, '/app/img')


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'practice makes perfect!'
    UPLOAD_FOLDER = upload_dir

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:marvinzns@localhost/webapi?charset=utf8'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:marvinzns@localhost/webapi?charset=utf8'


class ProductionConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:marvinzns@localhost/webapi?charset=utf8'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
