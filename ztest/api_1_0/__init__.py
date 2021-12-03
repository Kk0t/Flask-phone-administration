# -*- coding: utf-8 -*-
# @Time    : 2021/9/8 10:47
# @Author  : WuBingTai
from flask import Blueprint

# 创建蓝图对象

api = Blueprint('api_1_0', __name__)

from . import passport, phone, borrow
