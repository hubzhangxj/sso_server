# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django.db import connection
from django.forms import ModelForm
from django import forms
from UAMS.settings import DEBUG
from .models import Backup, Strategy
from utils.log import history
from utils.back import executor


class BackupForm(ModelForm):
    class Meta:
        model = Backup
        exclude = ()


def recovery(backup):
    return '<input type="button" value="数据还原" class="btn btn-warning" onclick="recovery(%s)"/>' % backup.id


recovery.allow_tags = True
recovery.short_description = '操作'


class BackupAdmin(admin.ModelAdmin):
    form = BackupForm
    list_display = ('date', 'path', recovery)

    @property
    def media(self):
        """
        hook原始加载脚本的逻辑，加入自定义的脚本
        :return:
        """
        extra = '' if DEBUG else '.min'
        js = [
            'core.js',
            'vendor/jquery/jquery%s.js' % extra,
            'jquery.init.js',
            'admin/RelatedObjectLookups.js',
            'actions%s.js' % extra,
            'urlify.js',
            'prepopulate%s.js' % extra,
            'vendor/xregexp/xregexp%s.js' % extra,
            # 以下是自定义的脚本
            'hook.js',
            'jquery.cookie.js',
            ]
        return forms.Media(js=['admin/js/%s' % url for url in js])


class StrategyForm(ModelForm):
    class Meta:
        model = Backup
        exclude = ()


class StrategyAdmin(admin.ModelAdmin):
    form = BackupForm
    list_display = ('name', 'hour', 'path', 'valid')

    def delete_model(self, request, obj):
        """
        如果当前生效的策略被删除时，将停止自动备份
        """
        if obj.valid:
            executor.stop()

        obj.delete()

    def save_model(self, request, obj, form, change):
        """
        当新增/修改策略时，确保只有一个策略生效
        """
        if not obj.id:
            action = '创建'
        else:
            action = '修改'

        obj.save()
        if obj.valid:  # 保证只有1个策略生效
            executor.start(obj)
            try:
                cursor = connection.cursor()
                sql = "UPDATE backup_strategy SET valid=FALSE WHERE id!=%s"
                cursor.execute(sql, [obj.id])
            finally:
                cursor.close()
        else:
            if Strategy.objects.filter(valid=True).count() < 1:
                executor.stop()

        history(request, request.user.username, '%s策略 %s' % (action, obj.name))

    @property
    def media(self):
        """
        hook原始加载脚本的逻辑，加入自定义的脚本
        :return:
        """
        extra = '' if DEBUG else '.min'
        js = [
            'core.js',
            'vendor/jquery/jquery%s.js' % extra,
            'jquery.init.js',
            'admin/RelatedObjectLookups.js',
            'actions%s.js' % extra,
            'urlify.js',
            'prepopulate%s.js' % extra,
            'vendor/xregexp/xregexp%s.js' % extra,
            # 以下是自定义的脚本
            'hook.js',
            'jquery.cookie.js',
            ]
        return forms.Media(js=['admin/js/%s' % url for url in js])


admin.site.register(Backup, BackupAdmin)
admin.site.register(Strategy, StrategyAdmin)
