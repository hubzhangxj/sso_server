# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from authen.models import APIKey


class Site(models.Model):
    """
    站点组
    """
    apikey = models.ForeignKey(APIKey)
    name = models.CharField('站点组名称', max_length=50, help_text='站点名称，最多50个字符')

    host = models.CharField(
        '主机地址', max_length=100, unique=True,
        help_text='站点主机地址，例如：www.yourhost.com或102.11.23.17:8000，最多100个字符',)
    default = models.BooleanField('默认分组', default=False, help_text='用户注册后默认加入该站点组')
    logout = models.CharField(
        '登出通知接口', max_length=200, blank=True,
        help_text='当账号登出时，UAMS将调用此接口通知站点。默认为http://主机地址/uams/logoutnotify ；最多200个字符')
    lock = models.CharField(
        '锁定通知接口', max_length=200, blank=True,
        help_text='当账号锁定超过7天时，UAMS将调用此接口通知站点。默认为http://主机地址/uams/locknotify ；最多200个字符')
    remarks = models.CharField('备注', max_length=200, blank=True, help_text='最多200个字符')

    class Meta:
        verbose_name = '站点组'
        verbose_name_plural = '站点组'

    def __unicode__(self):
        return unicode(self.name)


class Log(models.Model):
    """
    账号日志
    """
    ip = models.CharField(max_length=15)
    user = models.CharField(max_length=20)
    date = models.DateTimeField(auto_now_add=True, null=True)
    operation = models.CharField(max_length=50)
