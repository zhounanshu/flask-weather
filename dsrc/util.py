#!usr/bin/python
# -*- coding: utf-8 -*-

import logging

FORMAT = '%(asctime)s %(name)-6s %(levelname)-6s %(message)s'


def init_logging():
    logging.basicConfig(level=logging.DEBUG,
                        format=FORMAT,
                        datefmt="%a, %d %b %Y %H:%M:%S")
