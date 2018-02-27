# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django.db import connection
from django.forms import ModelForm
from backend.models import Site
from authen.models import APIKey
from utils.log import history


class SiteForm(ModelForm):
    class Meta:
        model = Site
        exclude = ('apikey', 'users')


class SiteAdmin(admin.ModelAdmin):
    form = SiteForm
    list_display = ('name', 'host', 'logout', 'lock', 'default', 'remarks', 'get_apikey', 'get_secret')

    def save_model(self, request, obj, form, change):
        """
        当创建站点时，自动分配apikey
        """
        if not obj.id:
            c = APIKey()
            c.save()
            obj.apikey = c
            action = '创建'
        else:
            action = '修改'

        history(request, request.user.username, '%s站点组 %s' % (action, obj.name))
        obj.save()

    def delete_model(self, request, obj):
        """
        删除site时，解除数据库中与account的关联
        """
        try:
            cursor = connection.cursor()
            sql = "DELETE FROM account_account_sites WHERE site_id = %s"
            cursor.execute(sql, [obj.id])
            history(request, request.user.username, '删除站点组 %s' % obj.name)
        finally:
            cursor.close()
        obj.delete()

    def get_apikey(self, obj):
        return obj.apikey.apikey

    def get_secret(self, obj):
        return obj.apikey.secret

    get_apikey.short_description = 'Api key'
    get_secret.short_description = 'Api secret'


admin.site.register(Site, SiteAdmin)
