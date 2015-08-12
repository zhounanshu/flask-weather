#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, request, g, jsonify, redirect, url_for, send_file
from flask.ext.restful import abort, Api, Resource
from flask.ext.httpauth import HTTPBasicAuth
# from flask.ext.socketio import SocketIO,emit,disconnect
from models import *
from werkzeug import secure_filename
import datetime, string, os
# import base64




app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()  # auth
#socketio = SocketIO(app)

#upload settings
UPLOAD_FOLDER = '/home/zwh/api-for-meteorological-data/image/content'
ALLOWED_EXTENSIONS = set(['png'])   # other extension can also be modified
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024    #max size is 1M

#verify the file type
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

#type change
def deviceDataToJson(value):
    list=[]
    for i in range (0,len(value)):
    #personal info are hidden
        dic={}
        dic['time'] = value[i].time.strftime("%Y-%m-%d %H:%M:%S")
        dic['longitude'] = value[i].longitude
        dic['latitude'] = value[i].latitude
        dic['temperature'] = value[i].temperature
        dic['humidity'] = value[i].humidity
        dic['uv'] = value[i].uv
        dic['pressure'] = value[i].pressure
        list.append(dic)
    return list


def userToJson(value):
    dic = {}
    dic['username'] = value.username
    dic['email'] = value.email
    dic['birthday'] = value.birthday
    if value.sex is True:
        dic['sex'] = "1"
    else:
        dic['sex'] = '0'
    dic['district'] = value.district
    dic['province'] = value.province
    dic['name'] = value.name
    dic['photo'] = value.portrait
    return dic


def ObservatoryDataToJson(value):
    list = []
    for i in range(0, len(value)):
        dic = {}
        dic['area'] = value[i].area
        dic['date'] = value[i].date.strftime("%Y-%m-%d")
        dic['temperature'] = value[i].temperature
        dic['weather'] = value[i].weather
        dic['uv'] = value[i].uv
        dic['humidity'] = value[i].humidity
        dic['windspeed'] = value[i].windspeed
        dic['winddirect'] = value[i].winddirect
        dic['pressure'] = value[i].pressure
        dic['sunrise'] = value[i].sunrise.time().strftime("%H:%M")
        dic['sunset'] = value[i].sunset.time().strftime("%H:%M")
        list.append(dic)
    return list


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
            slot = (day-day1).days
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
            lib["uv"] = str(int(uv[i]/uvNum[i]))
        result.append(lib)
        nowTime += datetime.timedelta(seconds=3600)

    return result


class ObDatas(Resource):
    def get(self):
        if not request.args or 'area' not in request.args or 'date' not in request.args or 'days' not in request.args:
            abort(404)

        area = request.args['area']
        date = request.args['date']
        days = string.atoi(request.args['days'])

        comingDate = datetime.datetime.strptime(date,'%Y-%m-%d') +
        datetime.timedelta(days = days)
        comingDateStr = comingDate.strftime("%Y-%m-%d")
        ulist = ObservatoryData.query.filter(ObservatoryData.date >= date, ObservatoryData.date <= comingDateStr , ObservatoryData.area == area ).all()
        list = []
        if len(ulist) == 0:
            abort(404)
        for i in range (0,days):
            list.append(ulist[i])
        return {'ObservatoryData':ObservatoryDataToJson(list)}

class realtimeDatas(Resource):
    def  get(self):
        currentTime = datetime.datetime.now()
        currentTimeStr = currentTime.strftime("%Y-%m-%d %H:%M:%S")
        priorTime = currentTime - datetime.timedelta(seconds = 3600)
        priorTimeStr = priorTime.strftime("%Y-%m-%d %H:%M:%S")
        ulist = DeviceData.query.filter(DeviceData.time >= priorTimeStr, DeviceData.time <= currentTimeStr).order_by(DeviceData.time).all()
        ulist = pickLastPost(ulist)
        if len(ulist) == 0:
            abort(404)
        return {'devicedata':deviceDataToJson(ulist)}

class shareDatas(Resource):
    def post(self):
        if not request.json:
            abort(400)
        else:
            json=request.json
            user_t = User.query.filter_by(id = json['id']).first_or_404()
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
            new_data=ShareData(time = json['time'], longitude = json['longitude'], latitude = json['latitude'], user = user_t, temperature = temperature, humidity = humidity,uv = uv, pressure = pressure)
            db.session.add(new_data)
            db.session.commit()
            return {'devicedata':json},201

class deviceDatas(Resource):
    def get(self):
        case = 0
        if len(request.args) == 2:
            if "id" in request.args and "mode" in request.args:
                if request.args["mode"] == "now":
                    case = 3
                #no use, get whole weeks' data
                #if request.args["mode"] == "week":
                #   case = 4
                if request.args["mode"] =="week":
                    case = 5
                if request.args["mode"] =="hour":
                    case = 6

        if case == 0:
            abort(400)

        if case == 3:
            #fetch friend's data atmost 1h earlier
            id= request.args['id']
            currentTime = datetime.datetime.now()
            priorTime = currentTime - datetime.timedelta( seconds = 3600)
            currentTimeStr = currentTime.strftime("%Y-%m-%d %H:%M:%S")
            priorTimeStr = priorTime.strftime("%Y-%m-%d %H:%M:%S")
            user = User.query.filter_by( id = id).first_or_404()
            ulist = user.datas.filter(DeviceData.time >= priorTimeStr, DeviceData.time <= currentTimeStr).order_by(DeviceData.time).all()
            ulist = pickLastPost(ulist)
            if len(ulist) == 0:
                abort(404)
            return {'devicedata':deviceDataToJson(ulist)},200

        if case == 5:
            id= request.args['id']
            currentTime = datetime.datetime.now()
            priorTime = (currentTime + datetime.timedelta( days = 1)).date() - datetime.timedelta( days = 7)
            currentTimeStr = currentTime.strftime("%Y-%m-%d %H:%M:%S")
            priorTimeStr = priorTime.strftime("%Y-%m-%d %H:%M:%S")
            user = User.query.filter_by( id = id).first_or_404()
            ulist = user.datas.filter(DeviceData.time >= priorTimeStr, DeviceData.time < currentTimeStr).order_by(DeviceData.time).all()
            #if len(ulist) == 0:
            #   abort(404)
            return {"devicedata":getAverageUV7days(ulist,priorTime,currentTime.date())}

        if case == 6:
            id= request.args['id']
            currentTime = datetime.datetime.now()
            priorTime = currentTime - datetime.timedelta( days = 1)
            currentTime = currentTime + datetime.timedelta(seconds = 3600)
            priorTime = priorTime + datetime.timedelta(seconds = 3600)

            currentTimeStr = currentTime.strftime("%Y-%m-%d %H:00:00")
            priorTimeStr = priorTime.strftime("%Y-%m-%d %H:00:00")
            user = User.query.filter_by( id = id).first_or_404()
            ulist = user.datas.filter(DeviceData.time >= priorTimeStr, DeviceData.time < currentTimeStr).order_by(DeviceData.time).all()
            #if len(ulist) == 0:
            #   abort(404)
            return {"devicedata":getAverageUV24hours(ulist,priorTime,currentTime)}


    def post(self):
        if not request.json:
            abort(400)
        else:
            json=request.json
            user_t = User.query.filter_by(id = json['id']).first_or_404()
            device_t = Device.query.filter_by(macId = json['macId']).first_or_404()
            new_data=DeviceData(time = json['time'], longitude = json['longitude'], latitude = json['latitude'], temperature = json['temperature'], humidity = json['humidity'],uv = json['uv'], pressure = json['pressure'], user = user_t, device = device_t)
            db.session.add(new_data)
            db.session.commit()
            return {'status': 'success'},201

class friend(Resource):
    def get(self,id):
        relationships = []
        relationships = Friendships.query.filter_by(user1_id = id).all()
        if len(relationships) == 0:
            abort(404)
        else :
            friendList = []
        for i in range(0,len(relationships)):
            friend = User.query.filter_by(id = relationships[i].user2_id).first()
            dic = {}
            dic['userId'] = friend.id
            dic['username'] = friend.username
            dic['photo'] = friend.portrait
            friendList.append(dic)
        return { "friends" : friendList } ,200

class friends(Resource):
    def post(self):
        if not request.json or 'username' not in request.json or 'friendname' not in request.json:
            abort(400)
        username1 = request.json['username']
        username2 = request.json['friendname']
        user1_id = User.query.filter_by(username = username1).first_or_404().id
        user2_id = User.query.filter_by(username = username2).first_or_404().id
        relation = Friendships.query.filter_by(user1_id = user1_id, user2_id = user2_id).first()
        if relation is None:
            newFriendship1 = Friendships(user1_id,user2_id)
            newFriendship2 = Friendships(user2_id,user1_id)
            db.session.add(newFriendship1)
            db.session.add(newFriendship2)
            db.session.commit()
            return {"status":"ok"},201
        else:
            return {"status":"error","message":"already been friends"},403

    def  delete(self):
        if not request.json or 'username' not in request.json or 'friendname' not in request.json:
            abort(400)
        username1 = request.json['username']
        username2 = request.json['friendname']
        user1_id = User.query.filter_by(username = username1).first_or_404().id
        user2_id = User.query.filter_by(username = username2).first_or_404().id
        relation1 = Friendships.query.filter_by(user1_id = user1_id,user2_id = user2_id).first()
        relation2 = Friendships.query.filter_by(user1_id = user2_id,user2_id = user1_id).first()
        if relation1 is None:
            return {"status":"error","message":"already not friends"},403
        else:
            db.session.delete(relation1)
            db.session.delete(relation2)
            db.session.commit()
            return {"status":"ok"},200

class device(Resource):
    def get(self,id):
        devices = []
        devices = Device.query.filter_by(userId = id).all()
        if len(devices) == 0:
            abort(404)
        else :
            macId = []
        for i in range(0,len(devices)):
            macId.append(devices[i].macId)
        return { "devices" :macId }

class devices(Resource):
    def post(self):
        if not request.json or 'macId' not in request.json or 'id' not in request.json:
            abort(400)
        id = request.json['id']
        macId = request.json['macId']
        user = User.query.filter_by(id = id).first_or_404()
        device = Device.query.filter_by(macId = macId).first()
        if device is not None:
            return {"status":"failed","message":"already add this device"},403
        else:
            newDevice = Device(macId, user)
            db.session.add(newDevice)
            db.session.commit()
            return {"status":"ok"},201
    def  delete(self):
        if not request.json or 'macId' not in request.json or 'id' not in request.json:
            abort(400)
        id = request.json['id']
        macId = request.json['macId']
        user = User.query.filter_by(id = id).first_or_404()
        device = Device.query.filter_by(macId = macId).first_or_404()
        db.session.delete(device)
        db.session.commit()
        return {"status":"ok"},200

class user(Resource):
    def  get(self,id):
        user = User.query.filter_by(id = id).first_or_404()
        return {"User":userToJson(user)},200

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
        people = User.query.filter_by(username = username).first()
        if people is None:
            newUser = User(username, password, email, name, birthday, province, district, sex)
            db.session.add(newUser)
            db.session.commit()
            userId = newUser.id

            return {"status": "ok","userId":userId,"location":"http//127.0.0.1:5000/image/content"},201
        else:
            return {"status":"failed","message": "Failed already has this username"}, 403

    def put(self):
        if len(request.json) <= 2 or 'id' not in request.json:
            abort(400)
        id = request.json['id']
        user = User.query.filter_by(id=id).first_or_404()
        if "username" in request.json:
            user_t = User.query.filter_by(
                username=request.json['username']).first()
            if user_t is None:
                user.username = request.json['username']
            else:
                return {
                    "status": "error", "message": "username has been used"}, 403
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


@app.route('/image/content/<filename>', methods=['GET'])
def portraits(filename):
    filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filename):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], "default.png")
    return send_file(filename, mimetype='image/png')


@app.route('/image/content', methods=['POST'])
def upload():
    file = request.files['file']
    userId = request.form['id']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filename = userId + '.' + filename.rsplit('.', 1)[1]
        user = User.query.filter_by(id=userId).first_or_404()
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        user.portrait = path
        db.session.commit()
        file.save(path)
        url_for('portraits', filename=filename)
        return jsonify({"status": "ok"})
    return redirect('/')


@app.route('/')
def index():
    return '''
    <!doctype html>
    <html>
    <body>
    <form action='/image/content' method='post' enctype='multipart/form-data'>
    <input type='file' name='file'>
    <input type='submit' value='Upload'>
    </form>
    '''


@app.route('/v1/login', methods=['GET'])
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    id = g.user.id
    return jsonify({'token': token.decode('ascii'), 'id': id})


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    # username_or_token = "sad"
    user = User.verify_auth_token(username_or_token)
    if not user:
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


# decorater to solve the cross domain problem
# cross domain resourse sharing, risks!
@app.after_request
def after_request(response):
    # response.headers.add('Access-Control-Allow-Origin', '*')
    # response.headers.add(
    #  'Access-Control-Allow-Headers','Content-Type,Authorization')
    # response.headers.add(
    #    'Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    # response.headers.add('Authorization','eyJhbGciOiJIUzI1NiIsImV4cCI6MTQzOTAzMjY0NSwiaWF0IjoxNDM4NDI3ODQ1fQ.eyJpZCI6Mn0.k7JDEPcsjGQMGpmzLcYJz4_FAAIBN_WU6uSMTrmq8n8')
    return response


api.add_resource(shareDatas, '/v1/sharedata')
api.add_resource(deviceDatas, '/v1/devicedata')
api.add_resource(realtimeDatas, '/v1/devicedata/realtime')
api.add_resource(devices, ' /v1/device')
api.add_resource(device, '/v1/device/<id>')
api.add_resource(users, '/v1/user')
# get user information
api.add_resource(user, '/v1/user/<id>')
api.add_resource(friends, '/v1/friend')
api.add_resource(friend, '/v1/friend/<id>')
api.add_resource(ObDatas, '/v1/weather')


if __name__ == '__main__':
    app.run(debug=True)
    # socketio.run(app)
