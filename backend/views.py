# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from account.models import Account
from utils import email
from utils.respone import response_json
from utils.log import logger, history
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import urllib2
from authen import UserTokenCache


def account_lock(request):
    """
    冻结账号
    """
    uid = request.POST.get("uid")
    try:
        account = Account.objects.get(id=uid)
        account.is_active = False
        account.date_locked = datetime.date.today()
        account.save()
        history(request, request.user.username, '锁定账号 %s' % account.username)
        email.send_email_for_locking(account.username, account.email)
        UserTokenCache.delete_user(account.username)
        # 通知各个站点
        opener = urllib2.build_opener()
        for site in account.sites.all():
            # 调用每个site接口
            try:
                # 临时做法，应加入二次调用验证后获取用户名的逻辑
                lock_notify = (site.lock if site.lock else ("http://" + site.host + "/uams/locknotify")) \
                                    + "?d=1&account=" + account.username
                logger.info("send locked request to site:" + lock_notify)
                opener.open(lock_notify, None)
            except Exception as e:
                logger.error('send locked request to site error:' + str(e))
                pass

        return response_json(None, None)
    except Exception as e:
        return response_json(e.message, None)


def account_unlock(request):
    """
    解冻账号
    """
    uid = request.POST.get("uid")
    try:
        account = Account.objects.get(id=uid)
        account.is_active = True
        account.save()
        history(request, request.user.username, '解锁账号 %s' % account.username)
        email.send_email_for_unlocking(account.username, account.email)
        return response_json(None, None)
    except Exception as e:
        return response_json(e.message, None)


schedule_locked_7_days = BackgroundScheduler()  # 账号锁定7天业务的定时任务


@schedule_locked_7_days.scheduled_job('cron', hour=2, minute=35)
def locked_7_days():
    logger.info('locked_7_days')
    locked_date = datetime.date.today() - datetime.timedelta(days=7)
    accounts = Account.objects.filter(is_active=False, date_locked=locked_date)
    sites_accounts = {}
    for account in accounts:
        for site in account.sites.all():
            if site in sites_accounts:
                sites_accounts[site].append(account.username)
            else:
                sites_accounts[site] = [account.username]

    opener = urllib2.build_opener()
    for site in sites_accounts:
        accounts = ','.join(sites_accounts[site])
        # 调用每个site接口
        logger.info("locked_7_days:" + site.name + ' -- ' + accounts)
        try:
            lock_7days_notify = (site.lock if site.lock else ("http://" + site.host + "/uams/locknotify")) \
                                + "?d=7&accounts=" + accounts
            logger.info("send locked_7_days request to site:" + lock_7days_notify)
            opener.open(lock_7days_notify, None)
        except Exception as e:
            logger.error(e)
            pass


schedule_locked_7_days.start()
