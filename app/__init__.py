#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.restful import Api
from views import *


def create_app(cnf):
    app = Flask(__name__)
    app.config.from_object(cnf)
    db.init_app(app)
    api = Api(app)
    api.add_resource(shareDatas, '/v1/sharedata')
    api.add_resource(deviceDatas, '/v1/devicedata')
    api.add_resource(realtimeDatas, '/v1/devicedata/realtime')
    api.add_resource(devices, '/v1/device')
    api.add_resource(device, '/v1/device/<id>')
    api.add_resource(users, '/v1/user')
    api.add_resource(user, '/v1/user/<id>')
    api.add_resource(friends, '/v1/friend')
    api.add_resource(friend, '/v1/friend/<id>')
    api.add_resource(ObDatas, '/v1/weather')

    return app
