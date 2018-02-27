# -*- coding: utf-8 -*-
import os
import hashlib
import urllib2
import json
from base64 import encodestring as encode
from utils.log import logger
from UAMS.settings import LDAP_SYNC_URL


create = {
    'JOBID': '98110',
    'OPERATION': 'add',
    'USERNAME': 'cn=admin,dc=open-estuary,dc=org',  # 登录ldap后台用户名
    'PASSWORD': 'huawei@123',    # 登录ldap后台密码
    'ADD_USERINFO': {
        'username': 'zhangxin',  # 你要操作的用户名
        'password': '{SSHA}r1FfyoE95vANVrbpxcuLh22eqEyvSGLp',  # 创建用户的密码
        'mail': 'zhangxin0329@thundersoft.com',  # 创建用户的邮箱
        'addDN': 'cn=zhangxin,ou=People,dc=open-estuary,dc=org'  # 此用户创建在哪个组织机构下
    }
}


update = {
    'JOBID': '98112',
    'OPERATION': 'update',
    'USERNAME': 'cn=admin,dc=open-estuary,dc=org',
    'PASSWORD': 'huawei@123',
    'UPDATE_USERINFO': {
        'deactiveDN': 'cn=XXXXX,ou=People,dc=open-estuary,dc=org',
        'userPassword': 'mynewpassword',
    }
}


def sync_user_to_ldap(username, password, email):
    """
    同步用户到ldap上
    :return:
    """
    if not LDAP_SYNC_URL or len(LDAP_SYNC_URL) < 1:
        return True
    create['ADD_USERINFO']['username'] = username
    create['ADD_USERINFO']['password'] = make_secret_for_ldap(password)
    create['ADD_USERINFO']['mail'] = email
    create['ADD_USERINFO']['addDN'] = 'cn=' + username + ',ou=People,dc=open-estuary,dc=org'

    headers = {'Content-Type': 'application/json'}
    logger.info('sync_user_to_ldap:' + username)
    request = urllib2.Request(LDAP_SYNC_URL, headers=headers, data=json.dumps(create))
    try:
        response = urllib2.urlopen(request, timeout=5)
        response = json.load(response)
        if response['RESULT'] == u'success':
            logger.info('sync_user_to_ldap: ok')
            return True
        else:
            logger.info('sync_user_to_ldap: error:' + response['ERROR_INFO'])
            return False
    except Exception as e:
        logger.info('sync_user_to_ldap: error:' + str(e))
        return False


def update_user_to_ldap(username, password):
    """
    同步用户到ldap上
    :return:
    """
    if not LDAP_SYNC_URL or len(LDAP_SYNC_URL) < 1:
        return True

    update['UPDATE_USERINFO']['userPassword'] = make_secret_for_ldap(password)
    update['UPDATE_USERINFO']['deactiveDN'] = 'cn=' + username + ',ou=People,dc=open-estuary,dc=org'

    headers = {'Content-Type': 'application/json'}
    logger.info('update_user_to_ldap:' + username)
    request = urllib2.Request(LDAP_SYNC_URL, headers=headers, data=json.dumps(update))
    try:
        response = urllib2.urlopen(request, timeout=5)
        response = json.load(response)
        if response['RESULT'] == u'success':
            logger.info('sync_user_to_ldap: ok')
            return True
        else:
            logger.info('update_user_to_ldap: error:' + response['ERROR_INFO'])
            return False
    except Exception as e:
        logger.info('update_user_to_ldap: error:' + str(e))
        return False


def make_secret_for_ldap(password):
    salt = os.urandom(4)
    h = hashlib.sha1(password)
    h.update(salt)
    return "{SSHA}" + encode(h.digest() + salt)


def random_secret():
    salt = os.urandom(4)
    h = hashlib.sha1(os.urandom(8))
    h.update(salt)
    return encode(h.digest() + salt)[3:11]
