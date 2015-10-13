#!/usr/bin/env python
# -*- coding: utf-8 -*-
import httplib
import logging
from config import loadConfig
from util import init_logging
import json
import sys
import MySQLdb
reload(sys)
sys.setdefaultencoding("utf-8")


class Meteor(object):

    def __init__(self, host=None, port=None, uri=None, **kwargs):
        init_logging()
        cnf = loadConfig()
        self.host = cnf.getHost()
        self.port = cnf.getPort()
        con = ''
        if kwargs:
            for key in kwargs:
                uriStr = ''
                uriStr = '&' + key + "=" + kwargs[key]
                con += uriStr
        self.uri = uri + con
        httpClient = None
        try:
            httpClient = httplib.HTTPConnection(
                self.host, self.port, timeout=30)
            httpClient.request('GET', self.uri)
            tmp = httpClient.getresponse().read()
            buf = json.loads(tmp)
            self.result = buf
        except:
            logging.debug('get data failed.....')
        finally:
            if httpClient:
                httpClient.close()

    def getResult(self):
        return self.result

uri = "/publicdata/data?appid=bFLKk0uV7IZvzcBoWJ1j&appkey=\
mXwnhDkYIG6S9iOyqsAW7vPVQ5ZxBe"

# connect database


def storeData(table, value):
    db_init = loadConfig()
    try:
        conn = MySQLdb.connect(host=db_init.db_host, charset='utf8',
                               user=db_init.db_user, passwd=db_init.db_passwd,
                               port=db_init.db_port, db=db_init.db)
        cur = conn.cursor()
        fields = '('
        s_fields = '('
        temp = []
        count = 0
        for key in value.keys():
            count += 1
            fields += key
            s_fields += '%s'
            if count == len(value):
                fields += ') values'
                s_fields += ')'
            else:
                fields += ','
                s_fields += ','
            temp.append(value[key])
        sql = 'insert into ' + table
        sql += fields
        sql += s_fields
        cur.execute(sql, temp)
        conn.commit()
        cur.close()
        conn.close()
    except:
        logging.debug("insert data failed......")


# store weather information for ten days
for_tenDay = Meteor(uri=uri, type='ten_day_forecast').getResult()
for forecast in for_tenDay:
    storeData("ten_day_forecast_data", forecast)

# store warnigs
warning = Meteor(uri=uri, type='warning_city').getResult()
# to do
# post data
#     pass

# store aqi information
aqi = Meteor(uri=uri, type='real_aqi').getResult()
storeData('aqi_data', aqi)

# store weather station information
stations = Meteor(uri=uri, type='sh_station').getResult()
for station in stations:
    storeData('station_data', station)

near_station = Meteor(
    uri=uri, type="autostation", jd='121.3213', wd='31.23444').getResult()
# print near_station
# print near_station[0]
# for value in near_station:
# to do
# post data
#     pass
