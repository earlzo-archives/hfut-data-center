# -*- coding:utf-8 -*-
from __future__ import unicode_literals
import logging

from baidu_lbs import LbsStorage, LbsApi
from config import BAIDU_LBS_AK, BAIDU_LBS_SK

hfut_stu_location_logger = logging.Logger('hfut-stu-location', level=logging.INFO)
hfut_stu_location_logger.addHandler(logging.StreamHandler())

lbs_storage = LbsStorage(BAIDU_LBS_AK, BAIDU_LBS_SK)
lbs_api = LbsApi(BAIDU_LBS_AK, BAIDU_LBS_SK)

