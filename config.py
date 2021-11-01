# -*- coding: utf-8 -*-
# @Time    : 2021/9/7 17:41
# @Author  : WuBingTai


class Config(object):
    '''项目的配置'''

    SECRET_KEY = "chNWJPzZzYWQWWrNauhULt31IuZcVG7OkE9kZaMojxVgtHVT3B3y0e9PRlI2GaK5"
    TOKEN_EXPIRATION = 60*60*12
    # 开启调试模式
    DEBUG = True
    # 数据库链接信息配置
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:ztest123@192.168.10.241:3306/flask_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # redis配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    EXPIRE_TIME = 60*60*12
    # Session 扩展的配置
    # SESSION_TYPE = "redis"  # 储存类型
    # SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # redis的链接
    # SESSION_USE_SIGNER = True  # 是否签名
    # PERMANENT_SESSION_LIFETIME = 86400  # 生命周期


class DevelopementConfig(Config):
    """开发阶段所需要的配置"""
    # 开启调试模式
    DEBUG = True


class PruductionConfig(Config):
    """生产环境下所需要的配置"""
    pass


config = {
    "development": DevelopementConfig,
    "production": PruductionConfig
}
