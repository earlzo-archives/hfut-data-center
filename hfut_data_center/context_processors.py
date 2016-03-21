# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from .forms import RegisterForm


def hfut_stu_location(request):
    if hasattr(request, 'login_form'):
        login_form = request.login_form
    else:
        login_form = AuthenticationForm()
    if hasattr(request, 'register_form'):
        register_form = request.register_form
    else:
        register_form = RegisterForm()
    if hasattr(request, 'password_reset_form'):
        password_reset_form = request.password_reset_form
    else:
        password_reset_form = PasswordResetForm()
    return dict(login_form=login_form, register_form=register_form, password_reset_form=password_reset_form)
