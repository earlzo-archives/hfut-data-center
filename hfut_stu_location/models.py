# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime

from django.core.validators import RegexValidator
from django.conf import settings
from django.db.models import Model, DateTimeField, CharField, URLField, BooleanField, OneToOneField, IntegerField, \
    EmailField, PositiveIntegerField
from django.utils import timezone

from hfut_stu_lib.lib import StuLib

from . import lbs_storage, lbs_api, hfut_stu_location_logger
from .config import GEOTABLE_ID


class UserInfo(Model):
    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = '用户信息表'

    UserModel = settings.AUTH_USER_MODEL
    user = OneToOneField(UserModel, related_name='user_info')
    stu_id = PositiveIntegerField('学号', unique=True,
                                  validators=[RegexValidator(r'\d{10}', '学号为10位数字')])
    id_card_number = CharField('身份证号', max_length=18, unique=True, null=True,
                               validators=[RegexValidator(r'\d{17}[xX\d]{1}', '身份证号格式不正确')],
                               editable=False)
    sys_password = CharField('教务系统密码', max_length=32)

    name = CharField('姓名', max_length=10, null=True)
    avatar = URLField('照片', null=True)
    sex = CharField('性别', max_length=1, choices=[('男', '男'), ('女', '女')], null=True)
    birthday = DateTimeField('生日', null=True)
    phone = CharField('联系电话', max_length=13, null=True, validators=[
        RegexValidator(r'\d{11}|\d{4}-\d{7}', '电话格式为11位数字或 0000-1234567')])
    home_phone = CharField('家庭电话', max_length=13, null=True, validators=[
        RegexValidator(r'\d{11}|\d{4}-\d{7}', '电话格式为11位数字或 0000-1234567')])

    high_school = CharField('毕业高中', max_length=20, null=True)
    college = CharField('学院简称', max_length=20, null=True)
    major = CharField('专业简称', max_length=20, null=True)
    klass = CharField('班级简称', max_length=20, null=True)

    nation = CharField('民族', max_length=10, null=True)
    native_place = CharField('籍贯', max_length=10, null=True)

    poi_id = IntegerField('poi数据id', unique=True, null=True)
    qq = IntegerField('QQ', unique=True, null=True,
                      validators=[RegexValidator(r'\d{5,15}', 'QQ号码最少为5位数字')])

    address = CharField('家庭地址', max_length=128, null=True)

    def sync_info_from_hfut(self):
        stu = StuLib(self.stu_id, self.sys_password)
        stu_info = stu.get_stu_info()
        res = lbs_storage.list_poi(GEOTABLE_ID, stu_id=','.join([unicode(self.stu_id), unicode(self.stu_id)]))
        if res['size'] == 1:
            lbs_storage.delete_poi(GEOTABLE_ID, res['pois'][0]['id'])
            hfut_stu_location_logger.warning('已存在学号为 {:d} 的 poi 数据, 已删除'.format(self.stu_id))
        loc = lbs_api.geocoding(stu_info['家庭地址'])['result']['location']
        res = lbs_storage.create_poi(GEOTABLE_ID, title='-'.join([stu_info['班级简称'], stu_info['姓名']]),
                                     latitude=loc['lat'], longitude=loc['lng'],
                                     address=stu_info['家庭地址'],
                                     avatar=stu_info['照片'],
                                     name=stu_info['姓名'],
                                     stu_id=stu.stu_id,
                                     sex=stu_info['性别'],
                                     high_school=stu_info['毕业高中'],
                                     college=stu_info['学院简称'],
                                     major=stu_info['专业简称'],
                                     klass=stu_info['班级简称'],
                                     tags=' '.join([stu_info['性别'],
                                                    stu_info['毕业高中'],
                                                    stu_info['学院简称'],
                                                    stu_info['专业简称'],
                                                    stu_info['班级简称']]))
        hfut_stu_location_logger.info('成功新建学号为 {:d} 的 poi 数据'.format(self.stu_id))
        self.poi_id = res['id']
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
        self.address = stu_info['家庭地址']
        self.save()

    def delete_data(self, with_poi=True):
        self.delete()
        if with_poi:
            lbs_storage.delete_poi(GEOTABLE_ID, self.poi_id)

    def filter_info_by_config(self):
        # todo: 完善详细资料获取功能
        info = {}
        if self.user_info_config.show_qq:
            info['QQ'] = self.qq
        if self.user_info_config.show_phone:
            info['联系电话'] = self.phone
        if self.user_info_config.show_home_phone:
            info['家庭电话'] = self.home_phone
        if self.user_info_config.show_birthday:
            info['生日'] = self.birthday
        if self.user_info_config.show_avatar:
            info['照片'] = self.avatar
        return info

    def __unicode__(self):
        return ' '.join([unicode(self.stu_id), self.name])


class UserInfoConfig(Model):
    class Meta:
        verbose_name = '用户配置'
        verbose_name_plural = '用户配置表'

    user_info = OneToOneField(UserInfo, related_name='user_info_config')
    address_last_changed_at = DateTimeField('地址上次修改时间', default=timezone.now, editable=False)
    # todo:默认显示 QQ 但是 QQ 默认为空
    show_qq = BooleanField('显示QQ', default=True)
    show_phone = BooleanField('显示联系电话', default=False)
    show_home_phone = BooleanField('显示家庭电话', default=False)
    show_avatar = BooleanField('显示照片', default=False)
    show_birthday = BooleanField('显示生日', default=False)


"""
字段名称    字段标识        字段类型
主键        geotable_id   uint64
名称        title         String(256)
地址        address       String(128)
经度        longitude     Double
纬度        latitude      Double

头像        avatar        url
学号        stu_id        int
姓名        name          string
性别        sex           string

中学        high_school   string
学院        college       string
专业        major         string
班级        klass         string

样式信息    icon_style_id string
"""
