# -*- coding: utf-8 -*-
"""
Created on Mon May 28 09:23:09 2018

@author: jpelda
"""
import logging
logging.basicConfig(filename='main.log', level=logging.DEBUG, filemode='w')
import time


def log_time(name, s_time):
    logging.info("{}; {}".format(name, time.time() - s_time))
    return time.time()
