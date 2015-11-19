#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint
from flask.ext.restful import Api

main = Blueprint('main', __name__)
api = Api(main)


from .views import *
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
api.add_resource(publicDatas, '/v1/publicdatas')

