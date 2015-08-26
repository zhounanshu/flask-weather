#!usr/bin/env python
# -*-coding: utf-8 -*-


class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'mysql://root:marvinzns@localhost/webapi?charset=utf8'
    SECRET_KEY = 'practice makes perfect!'
    UPLOAD_FOLDER = './path/to/upload'
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024


class ProducionConfig(Config):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'mysql://root:marvinzns@localhost/webapi?charset=utf8'
    SECRET_KEY = 'practice makes perfect!'
    UPLOAD_FOLDER = './path/to/upload'
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024


class DevelopConfig(Config):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'mysql://root:marvinzns@localhost/webapi?charset=utf8'
    SECRET_KEY = 'practice makes perfect!'
    UPLOAD_FOLDER = './path/to/upload'
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024


class TestConfig(Config):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'mysql://root:marvinzns@localhost/webapi?charset=utf8'
    SECRET_KEY = 'practice makes perfect!'
    UPLOAD_FOLDER = './path/to/upload'
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024
