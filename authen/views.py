# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import urlparse
import urllib2
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from backend.models import Site
from account.models import Account
from utils.respone import form_redirect
from utils.ldap import sync_user_to_ldap, update_user_to_ldap, random_secret
from utils.email import send_email_for_resetting, validate_email
from api import api_auth
from . import UserTokenCache, SSO_REQUEST_TOKEN_TTL
from utils.log import logger, history
from django.shortcuts import render


def blank(request):
    """
    为了火狐回退问题（backfix.js)
    """
    # return HttpResponse()
    return render(request, 'blank.html')


@api_auth
def api_authtoken(request):
    """
    提供给site进行验证token是否有效
    如果有效，则会把用户信息进行加密然后返回
    :param request:
    :return:有效的话则返回用户信息，无效则返回403
    """

    try:
        _auth_token = request.GET.get("auth_token")
        if _auth_token is None:
            return JsonResponse({"error": "参数缺失"}, status=403)

        # 验证token是否存在
        user = UserTokenCache.load(_auth_token)
        if not user:
            return JsonResponse({"error": "token不存在"}, status=403)

        return JsonResponse(user)
    except Exception as e:
        logger.error(e)
        return JsonResponse({"error": str(e)}, status=403)


def check_basic_params(callback, api_key, netloc):
    """
    检查基本参数
    :param callback
    :param api_key
    :param netloc
    :return:callback, api_key, resp403
    """

    if not (callback and api_key):
        logger.error('callback api_key为空')
        return HttpResponse("参数缺失", status=403), None
    # 验证host来源
    try:
        # TODO 开发时临时处理
        site = Site.objects.get(host=netloc)
        # site = Site.objects.filter(host=netloc, apikey__apikey=api_key).first()
        if site:
            return None, site
        else:
            raise Site.DoesNotExist
    except Site.DoesNotExist:
        logger.error("'"+netloc+"'不是合法站点")
        return HttpResponse("'"+netloc+"'不是合法站点", status=403), None


def get_basic_params(request):
    """
    获取并检查基本参数
    :param request:
    :return:callback, api_key, resp403
    """
    callback = request.POST.get("callback")
    api_key = request.POST.get("apikey")
    url_info_to = urlparse.urlparse(callback)
    error, site = check_basic_params(callback, api_key, url_info_to.netloc)
    if error:
        return None, None, None, error
    else:
        return callback, api_key, site, None


def resp_activate(request, user, site):
    return render(request, 'activate.html', {'user': user.username, 'site': site.name})


def activate(request):
    """
    激活
    """
    callback = request.session.get('callback')
    api_key = request.session.get('api_key')
    netloc = urlparse.urlparse(callback).netloc
    error, site = check_basic_params(callback, api_key, netloc)
    del request.session['callback']
    del request.session['api_key']
    if error:
        return error

    auth_token = request.session.get("auth_token", None)
    del request.session['auth_token']
    user = UserTokenCache.validate(request.META.get("REMOTE_ADDR"), auth_token)

    if not user:
        return 'user is not valid'

    if netloc not in user['sites']:  # 加入到已登录site中
        user['sites'].append(netloc)

    account = Account.objects.get(username=user['username'])
    account.sites.add(site)
    account.save()
    user['groups'].append(site.name)
    UserTokenCache.bind(auth_token, user)
    history(request, account.username, '激活 %s' % site.name)
    return form_redirect(callback, auth_token=auth_token)


@csrf_exempt
def login(request):
    """
    登录表单展示
    :param request:
    :return:
    """
    if request.method != "POST":
        logger.error('wrong method')
        return HttpResponse("wrong method", status=403)

    callback, api_key, site, error = get_basic_params(request)
    if api_key is None:  # callback或者api_key参数者无效
        logger.error(error)
        return error

    auth_token = request.COOKIES.get("auth_token")
    user = UserTokenCache.validate(request.META.get("REMOTE_ADDR"), auth_token)
    netloc = urlparse.urlparse(callback).netloc
    if user:  # 如果缓存中有合法的user，则表明登录过，直接跳转到callback，并携带token
        account = Account.objects.get(username=user['username'])

        if site not in account.sites.all():
            # 判断账号在当前站点是否已激活
            request.session['callback'] = callback
            request.session['api_key'] = api_key
            request.session['auth_token'] = auth_token
            return resp_activate(request, account, site)
        else:
            # 加入到已登录site中
            if netloc not in user['sites']:
                user['sites'].append(netloc)

        UserTokenCache.bind(auth_token, user)
        return form_redirect(callback, auth_token=auth_token)
    else:  # 未登录或者已过期，则显示登录界面
        context = {
            "form": AuthenticationForm(request),
            "next": callback,
            'site': get_current_site(request),
            "sso_timeout": SSO_REQUEST_TOKEN_TTL,
            "ssouser": user,
            "req": request,
            "error": request.POST.get("error", "")  # 在login_auth验证失败后，重定向到这里显示的错误信息
        }
        request.session['callback'] = callback
        request.session['api_key'] = api_key
        return render(request, 'login.html', context)


def login_auth(request):
    """
    登录表单验证
    :param request:
    :return:
    """
    if request.method != "POST":
        return HttpResponse("wrong method", status=403)

    callback = request.session.get('callback', None)
    api_key = request.session.get('api_key', None)
    try:
        netloc = urlparse.urlparse(callback).netloc
        error, site = check_basic_params(callback, api_key, netloc)
    except:
        error = "callback参数有误"

    if error:
        return error

    data = request.POST
    form = AuthenticationForm(request, data=data)
    if form.is_valid():  # 登录成功
        user = form.get_user()
        auth_token = UserTokenCache.add(request.META.get("REMOTE_ADDR"), user, netloc)  # 缓存用户账号
        # 判断账号在当前站点是否已激活
        if site not in user.sites.all():
            request.session['auth_token'] = auth_token
            return resp_activate(request, user, site)

        resp = form_redirect(callback, auth_token=auth_token)
        resp.set_cookie("auth_token", auth_token)  # NOTE: 这里的cookie是留到uams站点下的，并不是带给app site
        history(request, user.username, '登录 %s' % site.name)
        return resp
    else:
        # 检查是否是批量导入用户
        user = Account.objects.filter(username=request.POST.get("username", None)).first()
        if user:
            if not user.is_active:
                error = '很抱歉，该账号已被锁定，请联系管理员'
            else:
                data._mutable = True
                data['password'] = 'PWD_NEED_TO_BE_RESET'
                data._mutable = False
                form = AuthenticationForm(request, data=data)
                if form.is_valid():  # 验证成功，表明是批量导入的用户
                    error = "Your account is imported to UAMS newly, you need to reset your password."
                else:
                    error = '用户名与密码不匹配'
        else:
            error = '用户名与密码不匹配'
        # 跳转到登录界面
        resp = form_redirect('/uams/login', apikey=api_key, callback=callback, error=error)
        resp.delete_cookie("auth_token")
        return resp


@csrf_exempt
@api_auth
def user_auth(request):
    """
    用户验证接口
    :param request:
    :return:
    """
    data = request.GET
    form = AuthenticationForm(request, data=data)
    if form.is_valid():  # 登录成功
        return JsonResponse({'result': True}, status=200)
    else:
        return JsonResponse({'result': False},  status=200)


@csrf_exempt
def signup(request):
    """
    注册表单展示
    :param request:
    :return:
    """
    if request.method != "POST":
        return HttpResponse("wrong method", status=403)

    callback, api_key, site, error = get_basic_params(request)
    if api_key is None:  # callback或者api_key参数者无效
        print error
        return error

    context = {
        "username": request.POST.get("username", ""),
        "email": request.POST.get("email", ""),
        "error": request.POST.get("error", "")  # 验证失败后，重定向到这里显示的错误信息
    }
    request.session['callback'] = callback
    request.session['api_key'] = api_key
    return render(request, 'singup.html', context)


def signup_auth(request):
    """
    注册表单验证
    :param request:
    :return:
    """

    callback = request.session.get('callback')
    api_key = request.session.get('api_key')
    netloc = urlparse.urlparse(callback).netloc
    error, site = check_basic_params(callback, api_key, netloc)
    if error:
        return error

    username = request.POST.get("username")
    pwd = request.POST.get("pwd")
    pwd1 = request.POST.get("pwd1")
    email = request.POST.get("email")
    # TODO 加入更加细节的用户名密码验证，录入长度限制、特殊字符过滤等
    if not (username and pwd and pwd1 and email):
        return form_redirect('/uams/signup', apikey=api_key, callback=callback,
                             error='字段缺失')
    elif pwd != pwd1:
        return form_redirect('/uams/signup', apikey=api_key, callback=callback,
                             error='两次密码必须一致')
    elif not validate_email(email):
        return form_redirect('/uams/signup', apikey=api_key, callback=callback,
                             error='邮箱格式有误')

    user = Account.objects.filter(Q(username=username) | Q(email=email)).first()
    if user is None:  # 用户名可用
        result = sync_user_to_ldap(username, pwd, email)
        if result:
            user = Account(username=username, password=make_password(pwd, None, 'pbkdf2_sha256'), email=email)
            user.save()
            user.sites.add(*Site.objects.filter(default=True))  # 加入默认站点组
            user.sites.add(site)
            user.save()
            auth_token = UserTokenCache.add(request.META.get("REMOTE_ADDR"), user, netloc)  # 缓存用户账号
            resp = form_redirect(callback, auth_token=auth_token)
            resp.set_cookie("auth_token", auth_token)  # NOTE: 这里的cookie是留到ssoserver站点下的，并不是带给app site
            history(request, username, '注册 %s' % site.name)
            return resp
        else:
            error = '用户名已存在，同步到LDAP失败'
            # 跳转到注册界面
            return form_redirect('/uams/signup', apikey=api_key, callback=callback, username=username, email=email,
                                 error=error)

    else:
        error = '用户名已存在' if username == user.username else '邮箱已存在'
        # 跳转到注册界面
        return form_redirect('/uams/signup', apikey=api_key, callback=callback, username=username, email=email,
                             error=error)


@api_auth
def logout(request):
    """
    登出
    :param request:
    :return:
    """
    auth_token = request.GET.get("auth_token")
    client_ip = request.GET.get("client_ip")

    if not auth_token or not client_ip:  # auth_token参数者无效
        logger.warn('缺少登出参数')
        return JsonResponse({'msg': "缺少参数"}, status=403)

    user = UserTokenCache.validate(client_ip, auth_token)
    # referer = request.META.get("HTTP_REFERER")
    # netloc = urlparse.urlparse(referer).netloc if referer else None
    if user:  # 如果缓存中有合法的user，则依次访问已注册站点sso_logout_callback接口，携带用户名和token
        UserTokenCache.delete(auth_token)
        opener = urllib2.build_opener()
        for site in user['sites']:
            # if site != netloc:
            if site != client_ip:  # TODO 这里实际并不一定有效，因为site可能并不是ip
                try:
                    uams = Site.objects.get(host=site)
                    sso_logout_callback = (uams.logout if uams.logout else ("http://"+site + "/uams/logoutnotify")) \
                                          + "?auth_token=" + auth_token
                    logger.info("send logout request to site:" + sso_logout_callback)
                    opener.open(sso_logout_callback, None)
                except Exception as e:
                    logger.error('logout failed: ' + str(e))
                    pass
        history(client_ip, user['username'], '登出')
        return JsonResponse({'msg': "logouted."})
    else:  # 未登录或者已过期，则显示登录界面
        logger.error("token不存在")
        return JsonResponse({'msg': "token有误"}, status=403)


@csrf_exempt
def changepwd(request):
    """
    修改密码表单展示
    :param request:
    :return:
    """
    if request.method != "POST":
        return HttpResponse("wrong method", status=403)

    callback, api_key, site, error = get_basic_params(request)
    if api_key is None:  # callback或者api_key参数者无效
        logger.error(error)
        return error

    context = {
        "username": request.POST.get("username", ""),
        "error": request.POST.get("error", "")  # 验证失败后，重定向到这里显示的错误信息
    }
    request.session['callback'] = callback
    request.session['api_key'] = api_key
    return render(request, 'changepwd.html', context)


def changepwd_auth(request):
    """
    修改密码表单验证
    :param request:
    :return:
    """

    callback = request.session.get('callback')
    api_key = request.session.get('api_key')
    netloc = urlparse.urlparse(callback).netloc
    error, site = check_basic_params(callback, api_key, netloc)
    if error:
        return error

    username = request.POST.get("username")
    pwd = request.POST.get("password")
    pwd1 = request.POST.get("pwd1")
    pwd2 = request.POST.get("pwd2")
    # TODO 加入更加细节的用户名密码验证，录入长度限制、特殊字符过滤等
    if not (username and pwd and pwd1 and pwd2):
        return form_redirect('/uams/changepwd', apikey=api_key, callback=callback,
                             error='字段缺失')
    elif pwd2 != pwd1:
        return form_redirect('/uams/changepwd', apikey=api_key, callback=callback,
                             error='两次新密码不一致')
    elif pwd == pwd1:
        return form_redirect('/uams/changepwd', apikey=api_key, callback=callback,
                             error='新旧密码不能一样')

    form = AuthenticationForm(request, data=request.POST)
    if form.is_valid():  # 登录成功
        result = update_user_to_ldap(username, pwd1)
        if result:
            user = form.get_user()
            user.password = make_password(pwd1, None, 'pbkdf2_sha256')
            user.save()
            auth_token = UserTokenCache.add(request.META.get("REMOTE_ADDR"), user, netloc)  # 缓存用户账号
            resp = form_redirect(callback, auth_token=auth_token)
            resp.set_cookie("auth_token", auth_token)
            history(request, username, '修改密码')
            return resp
        else:
            return form_redirect('/uams/changepwd', apikey=api_key, callback=callback, username=username,
                                 error='同步到LDAP失败，请重试')
    else:
        return form_redirect('/uams/changepwd', apikey=api_key, callback=callback, username=username,
                             error='用户名与密码不匹配')


def resetpwd(request):
    """
    重置密码表单展示
    :param request:
    :return:
    """
    callback = request.session.get('callback')
    api_key = request.session.get('api_key')
    netloc = urlparse.urlparse(callback).netloc
    error, site = check_basic_params(callback, api_key, netloc)
    if error:
        return error
    context = {
        "username": request.POST.get("username", ""),
        "error": request.POST.get("error", "")  # 验证失败后，重定向到这里显示的错误信息
    }
    if request.method == "GET":
        return render(request, 'resetpwd.html', context)
    else:
        username = request.POST.get("username")
        email = request.POST.get("email")
        user = Account.objects.filter(username=username, email=email).first()

        if user:
            error = 'We have sent a email which contains a new password to you, please check your email.'
            context['error'] = error
            newpwd = random_secret()
            send_email_for_resetting(username, email, newpwd)
            user.password = make_password(newpwd, None, 'pbkdf2_sha256')
            user.save()
            resp = form_redirect('/uams/login', apikey=api_key, callback=callback, username=username, error=error)
            resp.delete_cookie("auth_token")
            logger.info('send email to ' + email)
            history(request, username, '重置密码')
            return resp
        else:
            context['error'] = '用户名和邮箱不匹配'
            return render(request, 'resetpwd.html', context)


