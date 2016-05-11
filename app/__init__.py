# -*- coding:utf-8 -*-
from __future__ import unicode_literals
import logging

from gaode_lbs_sdk import AMap
from .settings import AMAP_AK, AMAP_SK

logger = logging.Logger('hfut-data-center', level=logging.INFO)
logger.addHandler(logging.StreamHandler())

amap = AMap(AMAP_AK, AMAP_SK)
