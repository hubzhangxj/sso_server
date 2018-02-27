# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.apps import AppConfig

default_app_config = 'backup.BackupConfig'


class BackupConfig(AppConfig):
    name = 'backup'
    verbose_name = '备份管理'
