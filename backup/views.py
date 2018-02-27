# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import Strategy, Backup
from utils.respone import response_json
from utils.back import executor
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def count_valid_strategy(request):
    """
    检查当前启用的策略数量
    """
    return response_json(None, Strategy.objects.filter(valid=True).count())


def recovery(request):
    """
    还原
    """
    bid = request.POST.get("bid", None)
    if not bid:
        return response_json('缺少参数', None)

    try:
        backup = Backup.objects.get(id=bid)
        request.session['recovering'] = True
        executor.recovery(request, backup.path)
        request.session['recovering'] = False
        return response_json(None, 'starting')
    except:
        request.session['recovering'] = False
        return response_json('策略不存在', None)


def recovery_check(request):
    """
    还原状态检查
    """
    recovering = request.session.get('recovering', False)
    return response_json(None, recovering)


executor.start()
