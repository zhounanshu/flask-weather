#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (
    TimedJSONWebSignatureSerializer as
    Serializer, BadSignature, SignatureExpired)

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(500), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    birthday = db.Column(db.String(100), nullable=False)
    province = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    sex = db.Column(db.Boolean, nullable=False)
    portrait = db.Column(db.String(100))

    def __init__(
            self, username, password, email, name,
            birthday, province, district, sex, portrait=None):
        self.username = username
        self.password = password
        self.email = email
        self.name = name
        self.birthday = birthday
        self.province = province
        self.district = district
        self.sex = sex
        self.hash_password(password)
        self.portrait = portrait

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=3600 * 24 * 7):
        s = Serializer(expires_in=expiration)
        return s.dumps({'id': self.id})

    # only if the token is verified, can the user know the result
    @staticmethod
    def verify_auth_token(token):
        s = Serializer()
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data['id'])
        return user

    def __repr__(self):
        return '<User %r>' % self.username


class Friendships(db.Model):
    __tablename__ = 'friendships'
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, nullable=False)
    user2_id = db.Column(db.Integer, nullable=False)

    def __init__(self, user1_id, user2_id):
        self.user1_id = user1_id
        self.user2_id = user2_id

    def __repr__(self):
        return '<Friendship %r>' % self.id


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    macId = db.Column(db.String(100), unique=True, nullable=False)

    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship(
        'User', backref=db.backref('devices', lazy='dynamic'))

    def __init__(self, macId, user):
        self.macId = macId
        self.user = user

    def __repr__(self):
        return '<Device %r>' % self.id


class DeviceData(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    time = db.Column(db.DateTime, nullable=False)
    longitude = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.String(100), nullable=False)
    temperature = db.Column(db.String(100), nullable=False)
    humidity = db.Column(db.String(100), nullable=False)
    uv = db.Column(db.String(100), nullable=False)  # Ultraviolet rays
    pressure = db.Column(db.String(100), nullable=False)

    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    deviceID = db.Column(
        db.Integer, db.ForeignKey('device.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('datas', lazy='dynamic'))
    device = db.relationship(
        'Device', backref=db.backref('datas', lazy='dynamic'))

    def __init__(
            self, time, longitude, latitude, temperature,
            humidity, uv, pressure, user, device):
        self.time = time
        self.longitude = longitude
        self.latitude = latitude
        self.temperature = temperature
        self.humidity = humidity
        self.uv = uv
        self.pressure = pressure
        self.user = user
        self.device = device

    def __repr__(self):
        return '<DeviceData %r>' % self.id


class ShareData(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    time = db.Column(db.DateTime, nullable=False)
    longitude = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.String(100), nullable=False)
    temperature = db.Column(db.String(100))
    humidity = db.Column(db.String(100))
    uv = db.Column(db.String(100))  # Ultraviolet rays
    pressure = db.Column(db.String(100))

    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship(
        'User', backref=db.backref('sharedatas', lazy='dynamic'))

    def __init__(
            self, time, longitude, latitude, user,
            temperature=None, humidity=None,
            uv=None, pressure=None):
        self.time = time
        self.longitude = longitude
        self.latitude = latitude
        self.temperature = temperature
        self.humidity = humidity
        self.uv = uv
        self.pressure = pressure
        self.user = user

    def __repr__(self):
        return '<ShareData %r>' % self.id


class ObservatoryData(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    area = db.Column(db.String(100), nullable=False)
    temperature = db.Column(db.String(100), nullable=False)
    weather = db.Column(db.String(100), nullable=False)
    uv = db.Column(db.String(100), nullable=False)
    humidity = db.Column(db.String(100), nullable=False)
    windspeed = db.Column(db.String(100), nullable=False)
    winddirect = db.Column(db.String(100), nullable=False)
    pressure = db.Column(db.String(100), nullable=False)
    sunrise = db.Column(db.DateTime, nullable=False)
    sunset = db.Column(db.DateTime, nullable=False)
    date = db.Column(db.Date)

    def __init__(
            self, area, temperature, weather, uv,
            humidity, windspeed, winddirect, pressure,
            sunrise, sunset, date):
        self.area = area
        self.temperature = temperature
        self.weather = weather
        self.uv = uv
        self.humidity = humidity
        self.windspeed = windspeed
        self.winddirect = winddirect
        self.pressure = pressure
        self.sunrise = sunrise
        self.sunset = sunset
        if date is None:
            date = datetime.now().date()
        self.date = date

    def __repr__(self):
        return '<ObservatoryData %r>' % self.id
