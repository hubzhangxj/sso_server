# -*- coding: utf-8 -*-
import hmac
import hashlib
from django.conf import settings
from django.core.cache import cache
from utils.log import logger


def _load_setting(n, default):
    return getattr(settings, n) if hasattr(settings, n) else default


SSO_SEC_KEY = settings.SECRET_KEY
SSO_REQUEST_TOKEN_TTL = 1800  # 缓存30分钟
API_AUTH_ALLOWED_TIME_DRIFT = 300  # api时间戳允许得时间差5分钟


class UserTokenCache(object):
    @staticmethod
    def bind(token, user):
        cache.set(token, user, SSO_REQUEST_TOKEN_TTL)

    @staticmethod
    def load(token):
        return cache.get(token)

    @staticmethod
    def add(addr, user, netloc):
        token = UserTokenCache.generate(addr, user.username)
        groups = []
        for site in user.sites.all():
            groups.append(site.name)

        user = {"username": user.username, "email": user.email, "sites": [netloc], "groups": groups,
                "admin": user.site.name if user.site else None}
        cache.set(token, user, SSO_REQUEST_TOKEN_TTL)  # 缓存用户名
        cache.set(user['username'], token, SSO_REQUEST_TOKEN_TTL)  # 缓存用户名
        return token

    @staticmethod
    def generate(addr, username):
        val = addr+username
        result = hmac.new(str(SSO_SEC_KEY), val,  # uuid.uuid4().hex[:8]
                          digestmod=hashlib.sha256).hexdigest()
        logger.info("generate:" + val + "  " + result)

        return result

    @staticmethod
    def validate(addr, token):
        if not token:
            logger.info("token null")
            return None
        user = cache.get(token)
        if not user:  # 缓存中不存在或过期
            logger.info(token + " - token does not exist")
            return None
        gt = UserTokenCache.generate(addr, user['username'])
        # 缓存中有先前的登录信息，验证IP、username是否匹配
        if gt != token:  # 用户地址、用户名与登录时不一致
            logger.info(token + " - token is not valid")
            return None
        else:  # 一致
            return user

    @staticmethod
    def delete(token):
        user = cache.get(token)
        if user:
            cache.delete(user['username'])
        cache.delete(token)

    @staticmethod
    def delete_user(username):
        token = cache.get(username)
        if token:
            cache.delete(username)
            cache.delete(token)

    @staticmethod
    def clear():
        cache.clear()
