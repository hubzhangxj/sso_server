# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.apps import AppConfig

default_app_config = 'account.AccountConfig'


class AccountConfig(AppConfig):
    name = 'account'
    verbose_name = '账号管理'
