# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.encoding import force_text
import os, sys
from utils.log import logger


@deconstructible
class PathValidator(object):
    # message = '该路径不能访问，请输入可被www-data用户访问的绝对路径'
    message = '该路径不能访问，请输入合法的相对路径'
    code = 'invalid'

    def __init__(self, message=None, code=None):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        path = force_text(value)
        if path[0] == '/' or path.find(':') >= 0:
            raise ValidationError(self.message, code=self.code)
        try:
            path = os.path.join(sys.path[0], path)
            if not os.path.exists(path):
                os.makedirs(path)
            fp = os.path.join(path, 'JUST4TESTTSET4TSUJ')
            if os.path.exists(fp):
                os.rmdir(fp)
            os.mkdir(fp)
            if not os.path.exists(fp):
                raise ValidationError(self.message, code=self.code)
            else:
                os.rmdir(fp)
        except Exception as e:
            raise ValidationError(self.message, code=self.code)

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.limit_value == other.limit_value and
            self.message == other.message and
            self.code == other.code
        )

    def compare(self, a, b):
        return a is not b

    def clean(self, x):
        return x


class Strategy(models.Model):
    """
    备份策略
    """
    path_validator = PathValidator()
    name = models.CharField('策略名称', max_length=50, blank=False, default='备份策略', help_text='备份策略的名称')
    hour = models.IntegerField('执行时间(24h)', default=2, validators=[MinValueValidator(0), MaxValueValidator(23)],
                               help_text='自动执行备份的时间，24小时制，默认凌晨2点。')
    path = models.CharField('存储路径', max_length=200, blank=False, validators=[path_validator],
                            help_text='备份的存储路径（相对路径，位于UAMS部署路径下），例如：uams_bak')
    # path = models.CharField('存储路径', max_length=200, blank=False, validators=[path_validator],
    #                         help_text='备份的存储路径，请确保www-data用户（apache2创建）对该路径有访问权限。'
    #                                   '例如：/home/myname/uamsbaks/')
    valid = models.BooleanField('启用', default=False,
                                help_text='同一时间只允许1个策略处于启用中，启用1个则自动禁用其他策略。'
                                          '如果禁用全部策略，则无法执行自动备份（站点组和账号）命令。')

    class Meta:
        verbose_name = '备份策略'
        verbose_name_plural = '备份策略'


class Backup(models.Model):
    """
    备份
    """
    date = models.DateTimeField('备份日期', auto_now_add=True, null=True)
    path = models.CharField('存储路径', max_length=200, blank=False)

    class Meta:
        verbose_name = '数据备份'
        verbose_name_plural = '数据备份'
