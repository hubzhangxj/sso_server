# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import uuid
from django.db import models


def gen_apikey():
    return uuid.uuid4().hex[:8]


def gen_secret():
    return uuid.uuid4().hex


class APIKey(models.Model):
    class Meta:
        verbose_name = "API credential"

    apikey = models.CharField(max_length=8, default=gen_apikey, unique=True)
    secret = models.CharField(max_length=50, default=gen_secret)

    def __unicode__(self):
        return unicode(self.apikey)

    @staticmethod
    def permission_check(apikey, endpoint):
        try:
            ak = APIKey.objects.get(apikey=apikey)
            return ak.secret if ak else None
        except APIKey.DoesNotExist:
            pass
        return None
