# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from rest_framework import serializers
from hfut_stu_lib import StudentSession, GuestSession

campus = serializers.ChoiceField(label='校区', choices=(('XC', '宣城校区'), ('HF', '合肥校区')))
params = serializers.DictField(label='调用参数', default={})


class LoginSerializer(serializers.Serializer):
    username = serializers.IntegerField(label='学号', validators=[serializers.RegexValidator(r'\d{10}', '学号为10位数字')])
    password = serializers.CharField(label='教务系统密码', max_length=32)
    campus = campus


class IsHFUTAPI(object):
    message = '没有这个接口'
    code = 'invalid'

    def __init__(self, cls, message=None, code=None):
        self.cls = cls
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        action = getattr(self.cls, value, None)
        if action is None or not callable(action):
            raise serializers.ValidationError(self.message)


class StudentAPISerializer(serializers.Serializer):
    action = serializers.CharField(label='接口', validators=[IsHFUTAPI(StudentSession)])
    params = params


class GuestAPISerializer(serializers.Serializer):
    campus = campus
    action = serializers.CharField(label='接口', validators=[IsHFUTAPI(GuestSession)])
    params = params
