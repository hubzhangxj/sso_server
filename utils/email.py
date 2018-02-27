# -*- coding: utf-8 -*-

from UAMS import settings
from django.core.mail import EmailMultiAlternatives
from django.core.validators import EmailValidator


def send_email_for_resetting(username, email, pwd):
    print 'send_email_for_resetting '
    msg = EmailMultiAlternatives(settings.EMAIL_SUBJECT, settings.EMAIL_RESET_CONTENT.replace('USER', username)
                                 .replace('PWD', pwd), settings.EMAIL_DEFAULT_FROM, [email])
    msg.content_subtype = "html"
    msg.send()


def send_email_for_locking(username, email):
    print 'send_email_for_locking '
    msg = EmailMultiAlternatives(settings.EMAIL_SUBJECT, settings.EMAIL_LOCK_CONTENT.replace('USER', username),
                                 settings.EMAIL_DEFAULT_FROM, [email])
    msg.content_subtype = "html"
    msg.send()


def send_email_for_unlocking(username, email):
    print 'send_email_for_locking '
    msg = EmailMultiAlternatives(settings.EMAIL_SUBJECT, settings.EMAIL_UNLOCK_CONTENT.replace('USER', username),
                                 settings.EMAIL_DEFAULT_FROM, [email])
    msg.content_subtype = "html"
    msg.send()


def validate_email(email):
    """验证邮箱是否合法"""
    validator = EmailValidator()
    try:
        validator(email)
        return True
    except Exception as e:
        return False
