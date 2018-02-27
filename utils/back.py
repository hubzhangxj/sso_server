# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os, sys
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from utils.log import logger, history
from backup.models import Strategy, Backup
from UAMS.settings import DATABASES


class Backuper(object):
    __instance = None

    def __init__(self):
        self._scheduler = BackgroundScheduler()
        self._strategy = None
        self._job = None
        pass

    def __new__(cls, *args, **kwd):
        if Backuper.__instance is None:
            Backuper.__instance = object.__new__(cls, *args, **kwd)
        return Backuper.__instance

    def stop(self):
        """
        停止备份
        """

        if self._scheduler is None or self._job is None:
            return

        if self._scheduler.running:
            self._job.pause()

    def start(self, strategy=None):
        """
        启动备份
        """
        self.stop()
        if strategy and strategy.valid:
            hour = strategy.hour
        else:
            strategy = Strategy.objects.filter(valid=True).first()
            if strategy is None:
                return
            else:
                hour = strategy.hour

        minute = datetime.now().minute + 1
        if minute == 60:
            minute = 0
            hour += 1

        if not self._job:
            logger.info('new backup job @ %d:%d' % (hour, minute))
            self._job = self._scheduler.add_job(self._account_backup, 'cron'.encode('ascii'), hour=hour, minute=minute)
            self._scheduler.start()
        else:
            self._job.reschedule('cron'.encode('ascii'), hour=hour, minute=minute)
        self._strategy = strategy

    def _account_backup(self):
        path = os.path.join(sys.path[0], self._strategy.path, datetime.now().strftime("%Y_%m_%d_%H%M%S"))
        db = DATABASES['default']
        cmd = "mysqldump -u%s -p%s -h%s %s account_account account_account_sites backend_site > %s" % \
              (db['USER'], db['PASSWORD'], db['HOST'], db['NAME'], path)
        logger.info(cmd)
        os.system(cmd)
        backup = Backup(path=path)
        backup.save()
        history('UAMS', '系统', '自动备份')

    def recovery(self, request, path):
        logger.info('recovery')
        rec = BackgroundScheduler()
        time = datetime.now() + timedelta(seconds=0.2)
        history(request, request.user.username, '数据还原 ' + path)
        rec.add_job(self._recovery, 'date'.encode('ascii'), run_date=time, args=[path])
        rec.start()

    def _recovery(self, path):
        db = DATABASES['default']
        cmd = "mysql -u%s -p%s -h%s %s < %s" % \
              (db['USER'], db['PASSWORD'], db['HOST'], db['NAME'], path)
        logger.info(cmd)
        os.system(cmd)


executor = Backuper()






