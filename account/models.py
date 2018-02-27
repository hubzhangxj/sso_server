# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.validators import ASCIIUsernameValidator, UnicodeUsernameValidator
from django.utils import six, timezone
from backend.models import Site


class Account(AbstractBaseUser):
    """
    账号
    """
    username_validator = UnicodeUsernameValidator() if six.PY3 else ASCIIUsernameValidator()

    username = models.CharField(
        '用户名', max_length=20, unique=True, help_text='20个字符以内，只能由字母和数字组成',
        validators=[username_validator], error_messages={'unique': "用户名已存在"}
    )
    email = models.EmailField('邮箱地址', max_length=50, blank=False, unique=True,
                              error_messages={'unique': "邮箱已存在"})
    is_staff = models.BooleanField('登录后台', default=False, help_text='是否有登录后台的权限，请谨慎操作', )
    is_active = models.BooleanField('可登录', default=True, help_text='若被锁定将会无法登录')
    date_joined = models.DateTimeField('注册日期', default=timezone.now )
    date_locked = models.DateTimeField('锁定日期', null=True)
    sites = models.ManyToManyField(verbose_name='所属站点组', blank=True, to=Site, related_name='accounts')
    site = models.ForeignKey(Site, default=None, blank=True, null=True, verbose_name='管理站点',
                             related_name='site_in_charge', help_text='指定用户要管理的站点（作为超管），请谨慎操作。')
    is_superuser = models.BooleanField('超管', default=False, help_text='UAMS超级管理员',)
    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def has_perm(self, perm, obj=None):
        return self.is_active and self.is_superuser

    def has_perms(self, perm_list, obj=None):
        return self.is_active and self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_active and self.is_superuser

    def save(self, *args, **kwargs):
        return super(Account, self).save(*args, **kwargs)

    def get_full_name(self):
        return self.username.strip()

    def get_short_name(self):
        return self.username.strip()
