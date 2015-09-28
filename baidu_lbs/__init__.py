# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from baidu_lbs import *
from logging import Logger, INFO, StreamHandler

baidu_lbs_logger = Logger('baidu_lbs', level=INFO)
baidu_lbs_logger.addHandler(StreamHandler())
