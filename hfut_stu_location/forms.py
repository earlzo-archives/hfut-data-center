# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from Tkinter import Image
import re

from django.core.validators import RegexValidator
from django.forms import ModelForm, CharField, PasswordInput, TextInput, DateTimeInput, HiddenInput, NumberInput
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.forms.utils import ErrorList

from .models import UserInfoConfig, UserInfo
from hfut_stu_lib.lib import StuLib

UserModel = get_user_model()


class DivErrorList(ErrorList):
    def __str__(self):
        return self.as_div()

    def as_div(self):
        if not self:
            return ''
        error_div = '<div class="alert alert-danger" role="alert">' \
                    '<button type="button" class="close" data-dismiss="alert">&times;</button>' \
                    '{error:s}</div>'
        errors = ''.join([error_div.format(error=e) for e in self])
        return '<div class="errorlist">{:s}</div>'.format(errors)


class FormRender(ModelForm):
    def as_table(self):
        return self._html_output(
            normal_row='<tr%(html_class_attr)s><th>%(label)s</th><td>%(errors)s%(field)s%(help_text)s</td></tr>',
            error_row='<tr><td colspan="2">%s</td></tr>',
            row_ender='</td></tr>',
            help_text_html='<br /><span class="helptext">%s</span>',
            errors_on_separate_row=False)


class LoginForm(AuthenticationForm):
    username = CharField(label='用户名', max_length=254,
                         widget=TextInput({'class': 'form-control', 'placeholder': '用户名', 'required': True}))
    password = CharField(label="密码",
                         widget=PasswordInput({'class': 'form-control', 'placeholder': '密码', 'required': True}))


class RegisterForm(ModelForm):
    class Meta:
        model = UserModel
        fields = ('username',)
        widgets = {'username': TextInput({'placeholder': '用户名', 'class': 'form-control'})}

    error_messages = {
        'password_mismatch': '两次密码输入不一致',
        'sys_login_failed': '教务系统登陆失败，请验证你的学号和教务密码后重试',
        'wrong_stu_id_type': '学号格式不正确'
    }
    password = CharField(label='密码',
                         widget=PasswordInput({'placeholder': '密码',
                                               'class': 'form-control',
                                               'pattern': '\w{6,}'}))
    repeat_password = CharField(label='确认密码',
                                widget=PasswordInput({'placeholder': '确认密码',
                                                      'class': 'form-control',
                                                      'pattern': '\w{6,}'}))
    stu_id = CharField(label='学号',
                       validators=[RegexValidator(r'\d{10}')],
                       widget=TextInput({'placeholder': '学号',
                                         'class': 'form-control',
                                         'pattern': '\d{10}'}))
    sys_password = CharField(label='教务密码',
                             validators=[RegexValidator(r'[a-zA-Z0-9_]{6,16}', message='教务密码由6-16位字母数字或下划线组成')],
                             widget=PasswordInput({'placeholder': '教务密码',
                                                   'class': 'form-control',
                                                   'pattern': '[a-zA-Z0-9_]{6,16}'}))

    def clean(self):
        super(RegisterForm, self).clean()
        password = self.cleaned_data.get('password')
        repeat_password = self.cleaned_data.get('repeat_password')
        # 检查两次密码是否相同
        if password and repeat_password and password != repeat_password:
            self.add_error('password', self.error_messages['password_mismatch'])
            self.add_error('repeat_password', self.error_messages['password_mismatch'])
        # 检查教务系统账号是否能够登录
        if not re.match(r'\d{10}', self.cleaned_data.get('stu_id')):
            self.add_error('stu_id', self.error_messages['wrong_stu_id_type'])
        else:
            stu_id = int(self.cleaned_data.get('stu_id'))
            sys_password = self.cleaned_data.get('sys_password')
            try:
                StuLib(stu_id, sys_password)
            except ValueError:
                self.add_error('sys_password', self.error_messages['sys_login_failed'])
        return self.cleaned_data

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            # 初始化个人信息和隐私设置
            stu_id = int(self.cleaned_data.get('stu_id'))
            sys_password = self.cleaned_data.get('sys_password')
            try:
                user_info = UserInfo(user=user, stu_id=stu_id, sys_password=sys_password)
            except ValueError as e:
                pass
            else:
                user_info.save()
                user_info.sync_info_from_hfut()
                user_info_config = UserInfoConfig(user_info=user_info)
                user_info_config.save()
        return user


class PrivacyForm(ModelForm):
    class Meta:
        model = UserInfoConfig
        fields = '__all__'
        widgets = {'user_info': HiddenInput()}

    def __init__(self, *args, **kwargs):
        super(PrivacyForm, self).__init__(*args, **kwargs)
        # if self.instance and self.instance.pk:
        #     self.fields['user_info'].widget.attrs['readonly'] = True

    def clean_user_info(self):
        # instance 未作为初始化参数时为元类中的 model
        if self.instance and self.instance.pk:
            return self.instance.user_info
        else:
            return self.fields['user_info']

    def as_table(self):
        return self._html_output(
            normal_row='<tr%(html_class_attr)s><th>%(label)s</th><td>'
                       '<label class="toggle">%(field)s<span class="handle">%(errors)s</span></label>'
                       '%(help_text)s</td></tr>',
            error_row='<tr><td colspan="2">%s</td></tr>',
            row_ender='</td></tr>',
            help_text_html='<br /><span class="helptext">%s</span>',
            errors_on_separate_row=False)


class ProfileForm(ModelForm):
    class Meta:
        model = UserInfo
        exclude = ('poi_id',)
        widgets = {'user': HiddenInput(),
                   'stu_id': NumberInput({'class': "form-control",
                                          'pattern': "\d{10}",
                                          'required': True}),
                   'sys_password': PasswordInput({'class': "form-control",
                                                  'pattern': "\w{6,32}",
                                                  'required': True}, render_value=True),
                   'avatar': TextInput({'class': "form-control",
                                        'required': True}),
                   'birthday': DateTimeInput({'class': 'form-control'}),
                   'phone': TextInput({'class': "form-control",
                                       'pattern': "\d{11}|\d{4}-\d{7}"}),
                   'home_phone': TextInput({'class': "form-control",
                                            'pattern': "\d{11}|\d{4}-\d{7}"}),
                   'qq': TextInput({'class': "form-control",
                                    'pattern': "\d{5,13}"}),
                   'college': TextInput({'class': "form-control"}),
                   'major': TextInput({'class': "form-control"}),
                   'klass': TextInput({'class': "form-control"}),
                   'address': TextInput({'class': "form-control", 'required': True})}

    error_messages = {
        'password_mismatch': '两次密码输入不一致',
        'sys_login_failed': '教务系统登陆失败，请验证你的学号和教务密码后重试',
        'wrong_stu_id_type': '学号格式不正确'
    }

    disable_fields = ['name', 'sex', 'birthday', 'high_school', 'college', 'major', 'klass', 'nation', 'native_place']

    # todo: 还需完善
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        for field in self.disable_fields:
            self.fields[field].widget.attrs.update({'readonly': True, 'disable': True, 'class': 'form-control'})

    def clean(self):
        super(ProfileForm, self).clean()
        for field in self.disable_fields:
            self.cleaned_data[field] = getattr(self.instance, field)
        return self.cleaned_data

    def clean_user(self):
        if self.instance and self.instance.pk:
            return self.instance.user
        else:
            return self.fields['user']

    def clean_sys_password(self):
        stu_id = self.cleaned_data['stu_id']
        sys_password = self.cleaned_data['sys_password']
        try:
            StuLib(stu_id, sys_password)
        except ValueError:
            self.add_error('sys_password', self.error_messages['sys_login_failed'])
        return sys_password
