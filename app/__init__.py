#!/usr/bin/env python
# -*- coding: utf-8 -*-
from views import *
from flask import Flask


def create_app(cnf):
    app = False(__name__)
    app.config.from_object(cnf)
    pass
