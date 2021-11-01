# -*- coding: utf-8 -*-
# @Time    : 2021/9/15 10:55
# @Author  : WuBingTai
from flask import Blueprint, current_app, make_response
from flask_wtf.csrf import generate_csrf

web = Blueprint('web', __name__)


@web.route('/', defaults={'path': ''})
@web.route('/<path:path>')
def home(path):
    print(path)
    return current_app.send_static_file('index.html')

# @web.route('/<re(".*"):file_name>')
# def home(file_name):
#     """提供html静态文件"""
#     # 根据用户访问路径中指定的html文件名，找到指定静态文件并返回
#     if not file_name:
#         # 表示用户访问的是'/'
#         file_name = "index.html"
#
#     # # 判断如果不是网站logo
#     # if file_name != "favicon.ico":
#     #     # 拼接路径
#     #     file_name = "dist/" + file_name
#
#     # 生成csrf_token
#     # csrf_token = generate_csrf()
#     # 将csrf_token 设置到cookie中
#     response = make_response(current_app.send_static_file(file_name))
#     # response.set_cookie("csrf_token", csrf_token)
#     return response
#
# # @web.route('/')
# # def index():
# #     return current_app.send_static_file('index.html')
#
#
# @web.route('/<path:fallback>')
# def fallback(fallback):  # Vue Router 的 mode 为 'hash' 时可移除该方法
#     if fallback.startswith('css/') or fallback.startswith('js/') \
#             or fallback.startswith('img/') or fallback == 'favicon.ico':
#         return current_app.send_static_file(fallback)
#     else:
#         return current_app.send_static_file('index.html')
