# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db import transaction

# from .forms import RegisterForm, ProfileForm, PrivacyForm
from .models import StudentProfile


class IndexView(View):
    def get(self, request):
        # todo: 地图应当只有登陆后才能使用
        return render(request, 'index.html', dict(title='首页'))


class AboutView(View):
    def get(self, request):
        return render(request, 'about.html')

#
# class RegisterView(View):
#     template_name = 'register.html'
#
#     def get(self, request):
#         form = RegisterForm()
#         context = dict(form=form)
#         return render(request, self.template_name, context)
#
#     @transaction.atomic
#     def post(self, request):
#         form = RegisterForm(request.POST)
#         context = dict(form=form)
#         # forms = request.form
#         # challenge = forms.get('geetest_challenge')
#         # validate = forms.get('geetest_validate')
#         # seccode = forms.get('geetest_seccode')
#         # if gt.geetest_validate(challenge, validate, seccode) and login_form.validate_on_submit():
#         if form.is_valid():
#             return redirect('login')
#         else:
#             return render(request, self.template_name, context=dict(form=form))


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('IndexView')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LogoutView, self).dispatch(request, *args, **kwargs)


class StatisticsView(View):
    def get(self, request):
        return render(request, 'statistics.html')

#
# class ProfileView(View):
#     def get(self, request):
#         profile_form = ProfileForm(instance=request.user.user_info)
#         privacy_form = PrivacyForm(instance=request.user.user_info.user_info_config)
#         return render(request, 'profile.html', dict(profile_form=profile_form, privacy_form=privacy_form))
#
#     def post(self, request):
#         profile_form = ProfileForm(instance=request.user.user_info)
#         privacy_form = PrivacyForm(instance=request.user.user_info.user_info_config)
#         # is_submitted() 实际上只是判断了请求方法是否为 POST 或者 PUT ,
#         # 所以在页面中添加了一个 summit 表单来判断处理哪个表单
#         if request.POST['submit'] == 'profile':
#             profile_form = ProfileForm(request.POST, instance=request.user.user_info)
#             if profile_form.is_valid():
#                 if profile_form.has_changed():
#                     profile_form.save()
#                     messages.success(request, '资料修改成功！')
#                 else:
#                     messages.success(request, '没有修改任何资料！')
#             else:
#                 messages.error(request, '您提交的资料有误！')
#         elif request.POST['submit'] == 'privacy':
#             privacy_form = PrivacyForm(request.POST, instance=request.user.user_info.user_info_config)
#             # 加载隐私设置
#             if privacy_form.is_valid():
#                 privacy_form.save()
#                 messages.success(request, '隐私设置修改成功！')
#             else:
#                 messages.error(request, '您提交的设置有误！')
#         return render(request, 'profile.html', dict(profile_form=profile_form, privacy_form=privacy_form))
#
#     @method_decorator(login_required)
#     def dispatch(self, request, *args, **kwargs):
#         return super(ProfileView, self).dispatch(request, *args, **kwargs)
#

# ===== 后台接口相关 =====
class DetailInfoAPIView(View):
    def get(self, request):
        stu_id = request.GET.get('stu_id')
        info = {}
        if stu_id:
            try:
                stu = StudentProfile.objects.get(stu_id=stu_id)
            except StudentProfile.DoesNotExist:
                stu = None
            if stu:
                info = stu.filter_info_by_config()
        return JsonResponse(info)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(DetailInfoAPIView, self).dispatch(request, *args, **kwargs)
