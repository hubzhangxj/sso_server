# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
import logging
import datetime

reload(sys)
sys.setdefaultencoding('utf8')
logging.basicConfig()
logger = logging.getLogger('custom')


# class Logger:
#     def info(self, msg):
#         print datetime.datetime.now(), msg
#
#     def error(self, msg):
#         print datetime.datetime.now(), msg
#
#
# logger = Logger()


def history(ipOrReq, username, operation):
    """
    操作日志
    """
    from backend.models import Log
    if type(ipOrReq) != str and type(ipOrReq) != unicode:
        ipOrReq = ipOrReq.META.get("REMOTE_ADDR", '')
    log = Log(ip=ipOrReq, operation=operation, user=username)
    log.save()
