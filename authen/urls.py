from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^login$', views.login),
    url(r'^logout$', views.logout),
    url(r'^login_auth$', views.login_auth),
    url(r'^authuser$', views.user_auth),
    url(r'^activate$', views.activate),
    url(r'^authtoken$', views.api_authtoken),
    url(r'^signup$', views.signup),
    url(r'^signup_auth$', views.signup_auth),
    url(r'^changepwd$', views.changepwd),
    url(r'^changepwd_auth$', views.changepwd_auth),
    url(r'^resetpwd$', views.resetpwd),
    url(r'^blank', views.blank),

]
