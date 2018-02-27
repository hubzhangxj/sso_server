# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.apps import AppConfig


default_app_config = 'backend.BackendConfig'

sites_default = []  # 缓存新注册用户时的默认站点


class BackendConfig(AppConfig):
    name = 'backend'
    verbose_name = '后台管理'
