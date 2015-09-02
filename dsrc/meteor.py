#!/usr/bin/env python
# -*- coding: utf-8 -*-
import httplib
import logging
from config import loadConfig
from util import init_logging
import json
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


class Meteor(object):

    def __init__(self, host=None, port=None, uri=None, **kwargs):
        init_logging()
        cnf = loadConfig()
        self.host = cnf.getHost()
        print self.host
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


tenDay = Meteor(uri=uri, type='ten_day_forecast').getResult()
print tenDay[0]
# for value in tenDay:
#     # to do
#     # post data
#     pass

warning = Meteor(uri=uri, type='warning_city').getResult()
print warning
# for value in warnings:
#     # to do
#     # post data
#     pass

aqi = Meteor(uri=uri, type='real_aqi').getResult()
print aqi

station = Meteor(uri=uri, type='sh_station').getResult()
print station[0]
# for value in station:
#     # to do
#     # post data
#     pass

near_station = Meteor(
    uri=uri, type="autostation", jd='121.3213', wd='31.23444').getResult()
print near_station
# print near_station[0]
# for value in near_station:
#     # to do
#     # post data
#     pass
