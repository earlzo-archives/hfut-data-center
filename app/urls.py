# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import url

from .views import IndexView, LoginView, LogoutView, StudentAPIView, GuestAPIView
urlpatterns = [
    url(r'^$|^index', IndexView.as_view(), name='首页'),
    url(r'^api/login', LoginView.as_view(), name='登录'),
    url(r'^api/logout', LogoutView.as_view(), name='注销'),
    url(r'^hfut-api/student', StudentAPIView.as_view(), name='学生教务接口'),
    url(r'^hfut-api/guest', GuestAPIView.as_view(), name='公共教务接口'),
]

