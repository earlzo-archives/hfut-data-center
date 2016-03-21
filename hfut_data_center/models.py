# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function,unicode_literals

from datetime import datetime

from django.utils import six
from django.core.validators import RegexValidator
from django.conf import settings
from django.db import models

from hfut_stu_lib import AuthSession, STUDENT

from . import amap, hfut_stu_location_logger


class GeoAddress(models.Model):
    # 地址信息
    address = models.CharField('家庭地址', max_length=128)
    longitude = models.FloatField('经度', editable=False)
    latitude = models.FloatField('维度', editable=False)

    formatted_address = models.CharField('格式化地址', max_length=128, editable=False)
    province = models.CharField('省', max_length=56, editable=False)
    city = models.CharField('城市', max_length=56, editable=False)
    citycode = models.IntegerField('城市编码', editable=False)
    district = models.CharField('区域', max_length=56, editable=False)
    adcode = models.IntegerField('区域编码', editable=False)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        geo_result = amap.geo(self.address)
        if geo_result['count'] != '1':
            hfut_stu_location_logger.warning('不唯一的地理编码数据: %s', geo_result)

        first_result = geo_result['geocodes'][0]

        self.longitude, self.latitude = (float(v.strip()) for v in first_result['location'].split(','))
        self.formatted_address = first_result['formatted_address']
        self.province = first_result['province']
        self.city = first_result['city']
        self.citycode = first_result['citycode']
        self.district = first_result['district']
        self.adcode = first_result['adcode']

        super(GeoAddress, self).save(force_insert, force_update, using, update_fields)

    def __unicode__(self):
        return '<GeoAddress>[{:s]'.format(self.address)

    def __str__(self):
        return self.__unicode__()


class StudentProfile(models.Model):
    class Meta:
        verbose_name = '学生用户的资料'
        verbose_name_plural = '学生用户的资料表'

    UserModel = settings.AUTH_USER_MODEL
    user = models.OneToOneField(UserModel, related_name='student_profile')

    stu_id = models.IntegerField('学号', unique=True,
                                 validators=[RegexValidator(r'\d{10}', '学号为10位数字')])
    id_card_number = models.CharField('身份证号', max_length=18, unique=True, null=True,
                                      validators=[RegexValidator(r'\d{17}[xX\d]{1}', '身份证号格式不正确')],
                                      editable=False)
    sys_password = models.CharField('教务系统密码', max_length=32)

    name = models.CharField('姓名', max_length=10, null=True)
    avatar = models.URLField('照片', null=True)
    sex = models.CharField('性别', max_length=1, choices=[('男', '男'), ('女', '女')], null=True)
    birthday = models.DateTimeField('生日', null=True)
    phone = models.CharField('联系电话', max_length=13, null=True, validators=[
        RegexValidator(r'\d{11}|\d{4}-\d{7}', '电话格式为11位数字或 0000-1234567')])
    home_phone = models.CharField('家庭电话', max_length=13, null=True, validators=[
        RegexValidator(r'\d{11}|\d{4}-\d{7}', '电话格式为11位数字或 0000-1234567')])

    high_school = models.CharField('毕业高中', max_length=20, null=True)
    college = models.CharField('学院简称', max_length=20, null=True)
    major = models.CharField('专业简称', max_length=20, null=True)
    klass = models.CharField('班级简称', max_length=20, null=True)

    nation = models.CharField('民族', max_length=10, null=True)
    native_place = models.CharField('籍贯', max_length=10, null=True)

    qq = models.IntegerField('QQ', unique=True, null=True,
                             validators=[RegexValidator(r'\d{5,15}', 'QQ号码最少为5位数字')])

    # 地址信息
    address = models.OneToOneField(GeoAddress, related_name='student_profile')

    def sync_info_from_hfut(self):
        stu = AuthSession(self.stu_id, self.sys_password, STUDENT)
        stu_info = stu.get_stu_info()

        self.id_card_number = stu_info['身份证号']
        self.avatar = stu_info['照片']
        self.name = stu_info['姓名']
        self.sex = stu_info['性别']
        self.birthday = datetime.strptime(stu_info['出生日期'], '%Y-%m-%d')
        self.phone = stu_info['联系电话']
        self.home_phone = stu_info['家庭电话']
        self.high_school = stu_info['毕业高中']
        self.college = stu_info['学院简称']
        self.major = stu_info['专业简称']
        self.klass = stu_info['班级简称']
        self.nation = stu_info['民族']
        self.native_place = stu_info['籍贯']

        self.address = GeoAddress(address=stu_info['家庭地址'])
        self.save()

    def __unicode__(self):
        return '<StudentProfile>[{:d} {:s}]'.format(six.text_type(self.stu_id), self.name)

    def __str__(self):
        return self.__unicode__()
