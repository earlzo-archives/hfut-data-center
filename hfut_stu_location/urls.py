# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.views import login, logout, password_reset
from django.conf.urls import url

from .views import IndexView, AboutView, StatisticsView, ProfileView, DetailInfoAPIView, RegisterView
from .forms import LoginForm

urlpatterns = [
    url(r'^login', login, name='login', kwargs={'template_name': 'login.html', 'authentication_form': LoginForm}),
    url(r'^logout', logout, name='logout', kwargs={'next_page': 'index'}),
    url(r'^password_reset', password_reset, name='password_reset', kwargs={'template_name': 'password_reset.html'}),

    url(r'^$|^index', IndexView.as_view(), name='index'),
    url(r'^register', RegisterView.as_view(), name='register'),
    url(r'^about', AboutView.as_view(), name='about'),
    url(r'^profile', ProfileView.as_view(), name='profile'),
    url(r'^statistics', StatisticsView.as_view(), name='statistics'),
    url(r'^api/get_detail_info', DetailInfoAPIView.as_view(), name='get_detail_info'),
]
