# -*- coding: utf-8 -*-
# @Time    : 2021/9/8 11:14
# @Author  : WuBingTai
import functools

from itsdangerous import BadSignature, SignatureExpired
from werkzeug.routing import BaseConverter
from flask import session, jsonify, g, request

from ztest.utils.response_code import RET


class RegexConverter(BaseConverter):
    """自定义正则转换器"""

    def __init__(self, url_map, *args, **kwargs):
        super(RegexConverter, self).__init__(url_map)
        self.regex = args[0]


#
# def login_required(f):
#     """
#     用户是否登录的装饰器判断
#     :param f:
#     :return:
#     """
#
#     # 修饰内层函数，以防当前修饰器去修改被装饰函数的__name__属性
#     @functools.wraps(f)
#     def wrapper(*args, **kwargs):
#         user_id = session.get('user_id')
#         if not user_id:
#             return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
#         else:
#             g.user_id = user_id
#             return f(*args, **kwargs)
#
#     return wrapper


def login_required(token):
    """
    :param token:
    :return:
    """

    @functools.wraps(token)
    def wrapper(*args, **kwargs):
        if request.headers.get("Access-Token"):
            from ztest import s
            try:
                data = s.loads(request.headers.get("Access-Token"))
                g.user_id = data.get("id")
                g.user_name = data.get("name")

                # 判断Token是否已经在redis中过期
                from ztest import redis_store
                if redis_store.get(f"token_{data.get('id')}") is None:
                    return jsonify(errno=RET.AuthFailed, msg='token验证失败'), 401

                return token(*args, **kwargs)
            except BadSignature:
                return jsonify(errno=RET.AuthFailed, msg='token验证失败'), 403
            except SignatureExpired:
                return jsonify(errno=RET.AuthFailed, msg='token过期'), 403
        else:
            return jsonify(errno=RET.DBERR, msg='token为空'), 501

    return wrapper

# def verify_token(token):
#     @functools.wraps(token)
#     def wrapper(*args, **kwargs):
#         try:
#             from ztest import s
#             data = s.loads(token)
#         except BadSignature:
#             # AuthFailed 自定义的异常类型
#             raise RET.AuthFailed(msg='token不正确')
#         except SignatureExpired:
#             raise RET.AuthFailed(msg='token过期')
#             # 校验通过返回True
#         return token(*args, **kwargs)
#
#     return wrapper
