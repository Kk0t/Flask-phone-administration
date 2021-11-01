# -*- coding: utf-8 -*-
# @Time    : 2021/9/8 10:40
# @Author  : WuBingTai
import redis
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from itsdangerous import Serializer

from config import config
from ztest.utils.common import RegexConverter
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

# redis
redis_store = None
# 初始化SQLAlchemy
db = SQLAlchemy()
# 集成CSRF保护：提供了校验cookie中的csrf和表单中提交过来的csrf的是否一样
# csrf = CSRFProtect()

# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG)  # 调试debug级
# 创建日志记录器，指明日志的保存路径，每个日志文件的最大大小，保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
# 创建日志记录的格式               等级    输入日志信息的文件名    行数       日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（current_app）添加日志记录器
logging.getLogger().addHandler(file_log_handler)

s = None


def create_app(config_name):
    """工厂方法：根据传入的内容，生成指定内容所对应的对象"""

    app = Flask(__name__,
                template_folder="./static/dist",
                static_folder="./static/dist",
                static_url_path="")

    # 从对象中加载配置
    app.config.from_object(config[config_name])

    # 关联当期那app
    db.init_app(app)
    # csrf.init_app(app)    //暂时不需要

    # redis初始化
    global redis_store
    redis_store = redis.StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT)
    # 关联当前app
    # csrf.init_app(app)   //暂时不需要
    # 集成session
    # Session(app)
    # 向app中添加自定义的路由转换器
    app.url_map.converters['re'] = RegexConverter

    global s
    s = Serializer(config[config_name].SECRET_KEY, expires_in=config[config_name].TOKEN_EXPIRATION)

    # 注册蓝图，在使用的时候再引入
    from ztest.api_1_0 import api
    app.register_blueprint(api, url_prefix='/api/v1.0')
    # 注册html静态文件的蓝图
    from ztest import web
    app.register_blueprint(web.web)

    return app
