# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django.forms import ModelForm
from account.models import Account
from django import forms
from UAMS.settings import DEBUG
import backend.models
from django.contrib.auth.hashers import make_password


class AccountForm(ModelForm):
    class Meta:
        model = Account
        fields = ('username', 'email', "is_active", 'date_joined', 'sites', "site")


def lock(user):
    clazz = 'btn-info' if user.is_active else 'btn-warning'
    label = '锁定' if user.is_active else '解锁'
    func = 'lock' if user.is_active else 'unlock'
    return '<input type="button" value="%s" class="btn %s" onclick="%s(%s,\'%s\')"/>' \
           % (label, clazz, func, user.id, user.username)


lock.allow_tags = True
lock.short_description = '锁定操作'


def groups(user):
    sites_arr = []
    for s in user.sites.all():
        sites_arr.append(s.name)
    return ','.join(sites_arr)


groups.short_description = '所属站点组'


def site(user):
    return user.site.name if user.site else None


site.short_description = '管理的站点'


class AccountAdmin(admin.ModelAdmin):
    form = AccountForm
    list_display = ('username', 'email', groups, site, 'is_active', lock)
    search_fields = ('username', 'email')
    list_filter = ('is_active', 'site', 'sites')

    def save_model(self, request, obj, form, change):
        """
        当新增时，如果用户没有指定site，则归属默认site
        """
        if not obj.id:
            obj.password = make_password('zaq1xsw2', None, 'pbkdf2_sha256')
            if form.cleaned_data['sites'].count() < 1:
                form.cleaned_data['sites'] = backend.models.Site.objects.filter(default=True)
        obj.save()

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


admin.site.register(Account, AccountAdmin)
