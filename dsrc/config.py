#!/usr/bin/python env
# -*- coding: utf-8 -*-
from util import init_logging
import logging
import os
import json


class loadConfig(object):

    def __init__(self):
        init_logging()
        self.path = os.path.split(
            os.path.realpath(__file__))[0] + "/config.json"
        with open(self.path) as f:
            configInfor = json.load(f)
        if configInfor is not None:
            self.host = configInfor['host']
            self.port = configInfor['port']
            self.db_host = configInfor['db_host']
            self.db_port = configInfor['db_port']
            self.db_user = configInfor['db_user']
            self.db_passwd = configInfor['db_passwd']
            self.db = configInfor['db']
        else:
            logging.debug("load config failed.....")

    def getHost(self):
        return self.host

    def getPort(self):
        return self.port

    def get_dbHost(self):
        return self.db_host

    def get_dbPort(self):
        return self.db_port

    def get_dbUser(self):
        return self.db_user

    def get_dbPasswd(self):
        return self.db_passwd
