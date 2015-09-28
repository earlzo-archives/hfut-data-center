# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stu_id', models.PositiveIntegerField(unique=True, verbose_name='\u5b66\u53f7', validators=[django.core.validators.RegexValidator('\\d{10}', '\u5b66\u53f7\u4e3a10\u4f4d\u6570\u5b57')])),
                ('id_card_number', models.CharField(null=True, editable=False, max_length=18, validators=[django.core.validators.RegexValidator('\\d{17}[xX\\d]{1}', '\u8eab\u4efd\u8bc1\u53f7\u683c\u5f0f\u4e0d\u6b63\u786e')], unique=True, verbose_name='\u8eab\u4efd\u8bc1\u53f7')),
                ('sys_password', models.CharField(max_length=32, verbose_name='\u6559\u52a1\u7cfb\u7edf\u5bc6\u7801')),
                ('name', models.CharField(verbose_name='\u59d3\u540d', max_length=10, null=True, editable=False)),
                ('avatar', models.URLField(null=True, verbose_name='\u7167\u7247')),
                ('sex', models.CharField(verbose_name='\u6027\u522b', max_length=1, null=True, editable=False, choices=[('\u7537', '\u7537'), ('\u5973', '\u5973')])),
                ('birthday', models.DateTimeField(null=True, verbose_name='\u751f\u65e5')),
                ('phone', models.CharField(max_length=13, null=True, verbose_name='\u8054\u7cfb\u7535\u8bdd', validators=[django.core.validators.RegexValidator('\\d{11}|\\d{4}-\\d{7}', '\u7535\u8bdd\u683c\u5f0f\u4e3a11\u4f4d\u6570\u5b57\u6216 0000-1234567')])),
                ('home_phone', models.CharField(max_length=13, null=True, verbose_name='\u5bb6\u5ead\u7535\u8bdd', validators=[django.core.validators.RegexValidator('\\d{11}|\\d{4}-\\d{7}', '\u7535\u8bdd\u683c\u5f0f\u4e3a11\u4f4d\u6570\u5b57\u6216 0000-1234567')])),
                ('high_school', models.CharField(verbose_name='\u6bd5\u4e1a\u9ad8\u4e2d', max_length=20, null=True, editable=False)),
                ('college', models.CharField(max_length=20, null=True, verbose_name='\u5b66\u9662\u7b80\u79f0')),
                ('major', models.CharField(max_length=20, null=True, verbose_name='\u4e13\u4e1a\u7b80\u79f0')),
                ('klass', models.CharField(max_length=20, null=True, verbose_name='\u73ed\u7ea7\u7b80\u79f0')),
                ('nation', models.CharField(verbose_name='\u6c11\u65cf', max_length=10, null=True, editable=False)),
                ('native_place', models.CharField(verbose_name='\u7c4d\u8d2f', max_length=10, null=True, editable=False)),
                ('poi_id', models.IntegerField(unique=True, null=True, verbose_name='poi\u6570\u636eid')),
                ('qq', models.IntegerField(unique=True, null=True, verbose_name='QQ', validators=[django.core.validators.RegexValidator('\\d{5,15}', 'QQ\u53f7\u7801\u6700\u5c11\u4e3a5\u4f4d\u6570\u5b57')])),
                ('address', models.CharField(max_length=128, null=True, verbose_name='\u5bb6\u5ead\u5730\u5740')),
                ('user', models.OneToOneField(related_name='user_info', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '\u7528\u6237\u4fe1\u606f',
                'verbose_name_plural': '\u7528\u6237\u4fe1\u606f\u8868',
            },
        ),
        migrations.CreateModel(
            name='UserInfoConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address_last_changed_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\u5730\u5740\u4e0a\u6b21\u4fee\u6539\u65f6\u95f4', editable=False)),
                ('show_qq', models.BooleanField(default=True, verbose_name='\u663e\u793aQQ')),
                ('show_phone', models.BooleanField(default=False, verbose_name='\u663e\u793a\u8054\u7cfb\u7535\u8bdd')),
                ('show_home_phone', models.BooleanField(default=False, verbose_name='\u663e\u793a\u5bb6\u5ead\u7535\u8bdd')),
                ('show_avatar', models.BooleanField(default=False, verbose_name='\u663e\u793a\u7167\u7247')),
                ('show_birthday', models.BooleanField(default=False, verbose_name='\u663e\u793a\u751f\u65e5')),
                ('user_info', models.OneToOneField(related_name='user_info_config', to='hfut_stu_location.UserInfo')),
            ],
            options={
                'verbose_name': '\u7528\u6237\u914d\u7f6e',
                'verbose_name_plural': '\u7528\u6237\u914d\u7f6e\u8868',
            },
        ),
    ]
