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
        else:
            logging.debug("load config failed.....")

    def getHost(self):
        return self.host

    def getPort(self):
        return self.port

cnf = loadConfig()
