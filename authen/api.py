# -*- coding: utf-8 -*-
import hmac
import hashlib
import base64
import urllib
import urlparse
import time
from django.http import JsonResponse
from models import APIKey
from . import API_AUTH_ALLOWED_TIME_DRIFT


def api_auth_encrypt(sk, msg):
    dig = hmac.new(str(sk), msg, digestmod=hashlib.sha256).hexdigest()
    return base64.b64encode(dig).decode()


def _auth_url(url, body):
    url_parts = urlparse.urlparse(url)
    qs = urlparse.parse_qs(url_parts.query)
    sign = qs.get("signature", None)
    ak = qs.get("apikey", None)
    ts = qs.get("timestamp", None)

    qsl = filter(lambda x: x[0] != "signature", urlparse.parse_qsl(url_parts.query))

    if not (ak and sign and ts):
        raise Exception("parameter missing")

    # time stamp check, avoid replay attack
    if abs(time.time() - float(ts[0])) > API_AUTH_ALLOWED_TIME_DRIFT:
        raise Exception("time drift > %s sec" % API_AUTH_ALLOWED_TIME_DRIFT)

    sk = APIKey.permission_check(ak[0], url_parts.path.lstrip("/"))
    if not sk:  # user may be none
        raise Exception(ak[0] + " with " + url_parts.path.lstrip("/") + " entry point not allowed for the API key")

    orgiurl = urlparse.urlunparse(list(url_parts[0:4]) + [urllib.urlencode(qsl, True), ] + list(url_parts[5:]))
    if sign[0] != urllib.unquote_plus(api_auth_encrypt(sk, orgiurl+body if body else orgiurl)):
        raise Exception("signature error")
    return


def api_auth(function=None):
    """
    check:
    1, timestamp in reasonable range
    2, api key exists
    3, entry point allowed for this api key
    4, signature correctness

    effect:
    - add user object in request if the api key is binding with an user
    """
    def real_decorator(func):
        def wrapped(request, *args, **kwargs):
            try:
                _auth_url(request.get_full_path(), request.body)
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=403)
            return func(request, *args, **kwargs)
        setattr(wrapped, '__apiauth__', True)
        return wrapped
    return real_decorator if not function else real_decorator(function)
