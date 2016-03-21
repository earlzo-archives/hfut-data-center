# -*- coding:utf-8 -*-
from __future__ import unicode_literals
import logging

from gaode_lbs import AMap
from .settings import AMAP_AK, AMAP_SK

hfut_stu_location_logger = logging.Logger('hfut-stu-location', level=logging.INFO)
hfut_stu_location_logger.addHandler(logging.StreamHandler())

amap = AMap(AMAP_AK, AMAP_SK)
