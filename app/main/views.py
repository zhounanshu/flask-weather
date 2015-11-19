#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import request, g ,jsonify
from flask.ext.restful import abort, Resource, reqparse
from flask.ext.httpauth import HTTPBasicAuth
from PIL import Image
from werkzeug import secure_filename
import os


import datetime,urllib2
from randomData import *
from . import main
from .. import db
from .. models import *

auth = HTTPBasicAuth()


def to_json(model):
    """ Returns a JSON representation of an SQLAlchemy-backed object. """
    json = {}
    for col in model._sa_class_manager.mapper.mapped_table.columns:
        json[col.name] = str(getattr(model, col.name))
    return json


def to_json_list(model_list):
    json_list = []
    for model in model_list:
        json_list.append(to_json(model))
    return json_list


def pickLastPost(list):
    lib = {}
    newList = []
    for i in range(0, len(list)):
        data = list[i]
        location = (data.longitude, data.latitude)
        if location not in lib.keys():
            lib[location] = data
        else:
            if data.time > lib[location].time:
                lib[location] = data
    for i in lib.keys():
        newList.append(lib[i])
    return newList

def ObservatoryDataToJson(value):
    list = []
    for i in range(0, len(value)):
        dic = {}
        dic['area'] = value[i].area
        dic['date'] = value[i].date.strftime("%Y-%m-%d")
        dic['temperature'] = value[i].temperature
        dic['weather'] = value[i].weather
        dic['aqi'] = value[i].aqi
        dic['humidity'] = value[i].humidity
        dic['windspeed'] = value[i].windspeed
        dic['winddirect'] = value[i].winddirect
        dic['pressure'] = value[i].pressure
        dic['sunrise'] = value[i].sunrise.time().strftime("%H:%M")
        dic['sunset'] = value[i].sunset.time().strftime("%H:%M")
        list.append(dic)
    return list

def getAverageUV7days(list, day1, day2):
    dayNum = (day2 - day1).days + 1
    nowDay = day1
    time1 = datetime.datetime.strptime("10:00:00", '%H:%M:%S').time()
    time2 = datetime.datetime.strptime("15:00:00", '%H:%M:%S').time()
    uv = []
    uvNum = []
    result = []
    for i in range(0, dayNum):
        uv.append(0)
        uvNum.append(0)
    for i in range(0, len(list)):
        data = list[i]
        time = data.time.time()
        if time > time1 and time < time2:
            day = data.time.date()
            slot = (day - day1).days
            uv[slot] += string.atof(data.uv)
            uvNum[slot] += 1

    for i in range(0, dayNum):
        lib = {}
        nowDayStr = nowDay.strftime("%Y-%m-%d")
        lib["date"] = nowDayStr
        if uv[i] == 0:
            lib["uv"] = None
        else:
            lib["uv"] = str(int(uv[i] / uvNum[i]))
        result.append(lib)
        nowDay += datetime.timedelta(days=1)
    return result


def getAverageUV24hours(list, time1, time2):
    uvNum = []
    uv = []
    result = []
    timeStr1 = time1.strftime("%Y-%m-%d %H:00")
    hourFirst = time1.hour
    nowTime = datetime.datetime.strptime(timeStr1, '%Y-%m-%d %H:%M')
    for i in range(0, 24):
        uv.append(0)
        uvNum.append(0)

    for i in range(0, len(list)):
        data = list[i]
        time = data.time
        hour = time.hour
        if hour >= hourFirst:
            slot = hour - hourFirst
            uv[slot] += string.atof(data.uv)
            uvNum[slot] += 1
        else:
            slot = hour + 24 - hourFirst
            uv[slot] += string.atof(data.uv)
            uvNum[slot] += 1

    for i in range(0, 24):
        lib = {}
        nowTimeStr = nowTime.strftime("%Y-%m-%d %H:00")
        lib['time'] = nowTimeStr
        if uv[i] == 0:
            lib["uv"] = None
        else:
            lib["uv"] = str(int(uv[i] / uvNum[i]))
        result.append(lib)
        nowTime += datetime.timedelta(seconds=3600)

    return result


class ObDatas(Resource):

    def get(self):
        if not request.args or ('area' not in request.args) or ('date' not in request.args) or ('days' not in request.args):
            abort(404)
        area = request.args['area']
        date = request.args['date']
        days = string.atoi(request.args['days'])
        comingDate = datetime.datetime.strptime(
            date, '%Y-%m-%d') + datetime.timedelta(days=days)
        comingDateStr = comingDate.strftime("%Y-%m-%d")
        ulist = ObservatoryData.query.filter(
            ObservatoryData.date >= date,
            ObservatoryData.date <= comingDateStr,
            ObservatoryData.area == area).all()
        list = []
        if len(ulist) == 0:
            return {'data': []}
        for i in range(0, days):
            list.append(ulist[i])
        print list
        return {'data': to_json_list(ulist)}, 200


class realtimeDatas(Resource):

    def get(self):
        currentTime = datetime.datetime.now()
        currentTimeStr = currentTime.strftime("%Y-%m-%d %H:%M:%S")
        priorTime = currentTime - datetime.timedelta(seconds=3600)
        priorTimeStr = priorTime.strftime("%Y-%m-%d %H:%M:%S")
        ulist = DeviceData.query.filter(
            DeviceData.time >= priorTimeStr,
            DeviceData.time <= currentTimeStr).order_by(DeviceData.time).all()
        ulist = pickLastPost(ulist)
        if len(ulist) == 0:
            return {"data": []}
        return {"data": to_json_list(ulist)}, 200


class shareDatas(Resource):

    def post(self):
        if not request.json:
            abort(400)
        else:
            json = request.json
            user_t = User.query.filter_by(id=json['id']).first_or_404()
            if 'temperature' in json:
                temperature = json['temperature']
            else:
                temperature = None
            if 'humidity' in json:
                humidity = json['humidity']
            else:
                humidity = None
            if 'uv' in json:
                uv = json['uv']
            else:
                uv = None
            if 'pressure' in json:
                pressure = json['pressure']
            else:
                pressure = None
            new_data = ShareData(
                time=json['time'], longitude=json['longitude'],
                latitude=json['latitude'], user=user_t,
                temperature=temperature, humidity=humidity,
                uv=uv, pressure=pressure)
            db.session.add(new_data)
            db.session.commit()
            return {'status': 'ok'}, 201


class deviceDatas(Resource):

    def get(self):
        case = 0
        if len(request.args) == 2:
            if "id" in request.args and "mode" in request.args:
                if request.args["mode"] == "now":
                    case = 3
                # no use, get whole weeks' data
                # if request.args["mode"] == "week":
                #   case = 4
                if request.args["mode"] == "week":
                    case = 5
                if request.args["mode"] == "hour":
                    case = 6

        if case == 0:
            abort(400)

        elif case == 3:
            # fetch friend's data atmost 1h earlier
            id = request.args['id']
            currentTime = datetime.datetime.now()
            priorTime = currentTime - datetime.timedelta(seconds=3600)
            currentTimeStr = currentTime.strftime("%Y-%m-%d %H:%M:%S")
            priorTimeStr = priorTime.strftime("%Y-%m-%d %H:%M:%S")
            user = User.query.filter_by(id=id).first_or_404()
            ulist = user.datas.filter(
                DeviceData.time >= priorTimeStr,
                DeviceData.time <= currentTimeStr
            ).order_by(DeviceData.time).all()
            ulist = pickLastPost(ulist)
            if len(ulist) == 0:
                return{'data': []}
            return {'data': to_json_list(ulist)}, 200

        elif case == 5:
            id = request.args['id']
            currentTime = datetime.datetime.now()
            priorTime = (currentTime + datetime.timedelta(days=1)).date() - datetime.timedelta(days=7)
            currentTimeStr = currentTime.strftime("%Y-%m-%d %H:%M:%S")
            priorTimeStr = priorTime.strftime("%Y-%m-%d %H:%M:%S")
            user = User.query.filter_by(id=id).first_or_404()
            ulist = user.datas.filter(
                DeviceData.time >= priorTimeStr,
                DeviceData.time < currentTimeStr
            ).order_by(DeviceData.time).all()
            # if len(ulist) == 0:
            #   abort(404)
            return {"data": getAverageUV7days(
                ulist, priorTime, currentTime.date())}

        elif case == 6:
            id = request.args['id']
            currentTime = datetime.datetime.now()
            priorTime = currentTime - datetime.timedelta(days=1)
            currentTime = currentTime + datetime.timedelta(seconds=3600)
            priorTime = priorTime + datetime.timedelta(seconds=3600)

            currentTimeStr = currentTime.strftime("%Y-%m-%d %H:00:00")
            priorTimeStr = priorTime.strftime("%Y-%m-%d %H:00:00")
            user = User.query.filter_by(id=id).first_or_404()
            ulist = user.datas.filter(
                DeviceData.time >= priorTimeStr,
                DeviceData.time < currentTimeStr
            ).order_by(DeviceData.time).all()
            # if len(ulist) == 0:
            #   abort(404)
            return {"data": getAverageUV24hours(
                ulist, priorTime, currentTime)}

    def post(self):
        if not request.json:
            abort(400)
        else:
            json = request.json
            user_t = User.query.filter_by(id=json['id']).first_or_404()
            device_t = Device.query.filter_by(
                macId=json['macId']).first_or_404()
            new_data = DeviceData(
                time=json['time'],
                longitude=json['longitude'],
                latitude=json['latitude'],
                temperature=json['temperature'],
                humidity=json['humidity'],
                uv=json['uv'],
                pressure=json['pressure'],
                user=user_t,
                device=device_t)
            db.session.add(new_data)
            db.session.commit()
            return {'status':  'success'}, 201


class friend(Resource):

    def get(self, id):
        relationships = []
        relationships = Friendships.query.filter_by(user1_id=id).all()
        if len(relationships) == 0:
            abort(404)
        else:
            friendList = []
        for i in range(0, len(relationships)):
            friend = User.query.filter_by(id=relationships[i].user2_id).first()
            dic = {}
            dic['userId'] = friend.id
            dic['username'] = friend.username
            dic['photo'] = friend.portrait
            friendList.append(dic)
        return {"friends": friendList}, 200


class friends(Resource):

    def post(self):
        if not request.json or 'username' not in request.json or 'friendname' not in request.json:
            abort(400)
        username1 = request.json['username']
        username2 = request.json['friendname']
        user1_id = User.query.filter_by(username=username1).first_or_404().id
        user2_id = User.query.filter_by(username=username2).first_or_404().id
        relation = Friendships.query.filter_by(
            user1_id=user1_id, user2_id=user2_id).first()
        if relation is None:
            newFriendship1 = Friendships(user1_id, user2_id)
            newFriendship2 = Friendships(user2_id, user1_id)
            db.session.add(newFriendship1)
            db.session.add(newFriendship2)
            db.session.commit()
            return {"status": "ok"}, 201
        else:
            return {
                "status": "error", "message": "already been friends"}, 403

    def delete(self):
        if not request.json or 'username' not in request.json or 'friendname' not in request.json:
            abort(400)
        username1 = request.json['username']
        username2 = request.json['friendname']
        user1_id = User.query.filter_by(username=username1).first_or_404().id
        user2_id = User.query.filter_by(username=username2).first_or_404().id
        relation1 = Friendships.query.filter_by(
            user1_id=user1_id, user2_id=user2_id).first()
        relation2 = Friendships.query.filter_by(
            user1_id=user2_id, user2_id=user1_id).first()
        if relation1 is None:
            return {"status": "error", "message": "already not friends"}, 403
        else:
            db.session.delete(relation1)
            db.session.delete(relation2)
            db.session.commit()
            return {"status": "ok"}, 200


class device(Resource):

    def get(self, id):
        devices = []
        devices = Device.query.filter_by(userId=id).all()
        if len(devices) == 0:
            abort(404)
        else:
            macId = []
        for i in range(0, len(devices)):
            macId.append(devices[i].macId)
        return {"devices": macId}


class devices(Resource):

    def post(self):
        if not request.json or 'macId' not in request.json or 'id' not in request.json:
            abort(400)
        id = request.json['id']
        macId = request.json['macId']
        user = User.query.filter_by(id=id).first_or_404()
        device = Device.query.filter_by(macId=macId).first()
        if device is not None:
            return {
                "status": "failed", "message": "already add this device"}, 403
        else:
            newDevice = Device(macId, user)
            db.session.add(newDevice)
            db.session.commit()
            return {"status": "ok"}, 201

    def delete(self):
        if not request.json or 'macId' not in request.json or 'id' not in request.json:
            abort(400)
        id = request.json['id']
        macId = request.json['macId']
        user = User.query.filter_by(id=id).first_or_404()
        device = Device.query.filter_by(macId=macId).first_or_404()
        db.session.delete(device)
        db.session.commit()
        return {"status": "ok"}, 200


class user(Resource):
    def get(self, id):
        user = User.query.filter_by(id=id).first()
        userInfor = {}
        userInfor['username'] = user.username
        userInfor['email'] = user.email
        userInfor['birthday'] = user.birthday
        userInfor['province'] = user.province
        userInfor['district'] = user.district
        userInfor['sex'] = user.sex
        print user.sex
        if user is None:
            return {"data": {}}
        return {"data": userInfor}, 200


class users(Resource):

    def post(self):
        if not request.json:
            abort(400)
        username = request.json['username']
        password = request.json['password']
        birthday = request.json['birthday']
        name = request.json['name']
        email = request.json['email']
        province = request.json['province']
        district = request.json['district']
        sex = request.json['sex']
        people = User.query.filter_by(username=username).first()
        if people is None:
            newUser = User(
                username, password, email, name,
                birthday, province, district, sex)
            db.session.add(newUser)
            db.session.commit()
            userId = newUser.id
            return {
                "status": "ok",
                "userId": userId}, 201
        else:
            return {"status": "failed",
                    "message": "Failed already has this username"}, 403

    def put(self):
        if len(request.json) <= 2 or 'userId' not in request.json:
            abort(400)
        id = request.json['userId']
        user = User.query.filter_by(id=id).first_or_404()
        if "username" in request.json:
            user_t = User.query.filter_by(
                username=request.json['username']).first()
            if user_t is None:
                user.username = request.json['username']
            else:
                return {
                    "status": "error", "message": "username has been used"
                }, 403
        if "password" in request.json:
            user.password = request.json['password']
            user.hash_password(user.password)
        if "birthday" in request.json:
            user.birthday = request.json['birthday']
        if "email" in request.json:
            user.email = request.json['email']
        if "province" in request.json:
            user.province = request.json['province']
        if "district" in request.json:
            user.district = request.json['district']
        if "sex" in request.json:
            user.sex = request.json['sex']
        if "name" in request.json:
            user.name = request.json['name']
        db.session.commit()
        return {"status": "ok"}, 200


class publicDatas(Resource):

    def post(self):
        if not request.json or not request.args or ('type' not in request.args):
            abort(404)
        type = request.args['type']
        if type == "ten_day_forecast":
            for i in range(0,9):
                data = request.json['data'][i]
                datatime = data['datatime']
                oldData = TenDayForecastData.query.filter_by(datatime=datatime).first()
                if oldData is None:
                    direction = data['direction']
                    speed = data['speed']
                    tempe = data['tempe']
                    weather = data['weather']
                    weatherpic = data['weatherpic']
                    newData = TenDayForecastData(
                        datatime, direction, speed,
                        tempe, weather, weatherpic)
                    db.session.add(newData)
                else:
                    oldData.direction = data['direction']
                    oldData.speed = data['speed']
                    oldData.tempe = data['tempe']
                    oldData.weather = data['weather']
                    oldData.weatherpic = data['weatherpic']
            db.session.commit()
            return {"status": "ok"}, 201
        elif type == "warning_city":
            data = request.json['data'][0]
            publishtime = data['publishtime']
            warningtype = data['type']
            level = data['level']
            content = data['content']
            newWarningData = WarningData(
                publishtime,warningtype,level,content)
            db.session.add(newWarningData)
            db.session.commit()
            return {"status": "ok"}, 201
        elif type == "real_aqi":
            datetime = request.json['datetime']
            aqi = request.json['aqi']
            level = request.json['level']
            pripoll = request.json['pripoll']
            content = request.json['content']
            measure = request.json['measure']
            print 2
            newAQIData = AQIData(
                datetime, aqi, level,
                pripoll, content, measure)
            db.session.add(newAQIData)
            db.session.commit()
            return {"status": "ok"}, 201
        elif type == "sh_station":
            datalist = request.json['data']
            for i in range(0,len(datalist)):
                data = datalist[i]
                datetime = data['datetime']
                name = data['name']
                sitenumber = data['sitenumber']
                tempe = data['tempe']
                rain = data['rain']
                wind_direction = data['wind_direction']
                wind_speed = data['wind_speed']
                visibility = data['visibility']
                humi = data['humi']
                pressure = data['pressure']
                newStationData = StationData(
                    datetime, name, sitenumber,
                    tempe, rain, wind_direction,wind_speed,
                    visibility,humi,pressure)
                db.session.add(newStationData)
            db.session.commit()
            return {"status": "ok"}, 201
        else :
            abort(400)


@main.route('/v1/weather/alarm',methods=['GET'])
def get_alarm():
    url = 'http://61.152.122.112:8080/publicdata/data?appid=bFLKk0uV7IZvzcBoWJ1j&appkey=mXwnhDkYIG6S9iOyqsAW7vPVQ5ZxBe&type=warning_city'
    response = urllib2.urlopen(url)
    content = response.read()[1:-1]#remove the [] in string
    return jsonify({"data": content})


@main.route('/v1/token', methods=['GET'])
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })


@main.route('/v1/login', methods=['GET'])
@auth.login_required
def login():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii'), 'status': 'ok'})


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username = username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True
    pass

UPLOAD_FOLDER = ''
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


def allowed_file(f):
    return '.' in f and f.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@main.route('/v1/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save('../img', filename)
        return {}

@main.route('/v1/initData', methods=['GET'])
def initData():
    db.drop_all()
    db.create_all()

    people = []
    username = randomUsername(50)
    password = randomPassword(50)
    email = randomEmail(50)
    name = randomUsername(50)
    birthday = randomBirthday(50)
    area = randomAreaTrue(50)
    sex = randomSex(50)
    for i in range(0,50):
        people.append(User(username[i],password[i],email[i],name[i],birthday[i],"Shanghai",area[i],sex[i]))


    device = []
    macId = randomMacID(100)
    for i in range(0,50):
        device.append(Device(macId[i],people[i]))
    for i in range(50,100):
        device.append(Device(macId[i],people[random.randint(0,49)]))

    data = []
    date = randomDate(1000)
    longitude = randomValue(1000,0,0.01)
    latitude = randomValue(1000,0,0.01)
    temperature = randomValue(1000,0,40)
    humidity = randomValue(1000,0,40)
    uv = randomValue(1000,0,500)
    pressure = randomValue(1000,0,500)

    for i in range(0,50):
        data.append(DeviceData(date[i],longitude[i],latitude[i],temperature[i],humidity[i],uv[i],pressure[i],people[i],device[i]))
    for i in range(50,1000):
        x= random.randint(0,49)
        data.append(DeviceData(date[i],longitude[i],latitude[i],temperature[i],humidity[i],uv[i],pressure[i],people[x],device[x]))

    obData = []
    area = randomArea(1000)
    temperature = randomValue(1000,0,40)
    weather = randomWether(1000)
    aqi = randomValue(1000,0,500)
    humidity = randomValue(1000,0,500)
    windspeed = randomValue(1000,0,500)
    winddirect = randomValue(1000,0,500)
    pressure = randomValue(1000,0,500)
    sunrise,sunset,uploadTime = randomSunTime(1000)

    print "start commit"
    for i in range(0,1000):
        obData.append(ObservatoryData(area[i],temperature[i],weather[i],aqi[i],humidity[i],windspeed[i],winddirect[i],pressure[i],sunrise[i],sunset[i],uploadTime[i]))


    x=Friendships(1,2)
    y=Friendships(1,3)
    db.session.add(x)
    db.session.add(y)
    db.session.commit()

    for i in range(0,50):
        db.session.add(people[i])
        db.session.commit()

    for i in range(0,100):
        db.session.add(device[i])
        db.session.commit()

    for i in range(0,1000):
        db.session.add(data[i])
        db.session.commit()

    for i in range(0,1000):
        db.session.add(obData[i])
        db.session.commit()

    return jsonify({ 'status': 'ok' })
