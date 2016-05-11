# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render
from django.views.generic import View
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from rest_framework.views import APIView

from hfut_stu_lib import StudentSession, GuestSession
from .models import Profile
from .serializers import LoginSerializer, StudentAPISerializer, GuestAPISerializer


class IndexView(View):
    def get(self, request):
        return render(request, 'index.html', dict(title='首页'))


class LoginView(APIView):
    @transaction.atomic
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            campus = serializer.validated_data['campus']
            try:
                stu = StudentSession(username, password, campus)
            except ValueError:
                return Response({'msg': '登陆失败, 请检查表单内容是否正确'}, HTTP_401_UNAUTHORIZED)
            try:
                user = User.objects.get(username=username)
                user.profile.sys_password = password
                user.profile.stu = stu
            except User.DoesNotExist:
                user = User.objects.create_user(username)
                profile = Profile.objects.create(user=user, sys_password=password, campus=campus)
                profile.stu = stu
                profile.sync_profile_from_hfut(stu)
            user.set_password(password)
            user.save()
            user = authenticate(username=username, password=password)
            user.stu = stu
            login(request, user)
            return Response({'msg': '登陆成功'})


class LogoutView(APIView):
    def get(self, request):
        logout(request)
        return Response({'msg': '注销成功'})


class StudentAPIView(LoginRequiredMixin, APIView):
    raise_exception = True

    def post(self, request):
        serializer = StudentAPISerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            action = getattr(request.user.profile.stu, serializer.validated_data['action'])
            try:
                rv = action(**serializer.validated_data['params']).data
                return Response(rv)
            except Exception as e:
                return Response({'msg': str(e)}, status=HTTP_400_BAD_REQUEST)


class GuestAPIView(APIView):
    def post(self, request):
        serializer = GuestAPISerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            action = getattr(GuestSession(serializer.validated_data['campus']), serializer.validated_data['action'])
            try:
                rv = action(**serializer.validated_data['params']).data
                return Response({'result': rv})
            except Exception as e:
                return Response({'msg': str(e)}, status=HTTP_400_BAD_REQUEST)
