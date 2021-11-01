# -*- coding: utf-8 -*-
# @Time    : 2021/9/8 10:54
# @Author  : WuBingTai
# 实现登录注册功能
from itsdangerous import BadSignature, SignatureExpired

from ztest.constants import LOGIN_REDIS_EXPIRES
from . import api
from flask import request, current_app, jsonify, session, g
from ztest import redis_store, db, s
from ztest.models import User
from ztest.utils.response_code import RET
from ztest.utils.common import login_required


@api.route("/checkUserLogin")
def check_user_login():
    '''
    判断用户是否登录,如果登录,返回登录的信息:用户名,用户id
    :return:
    '''
    if request.headers.get("Access-Token"):
        try:
            data = s.loads(request.headers.get("Access-Token"))
            user_id = data.get("id")
            name = data.get("name")
        except BadSignature:
            return jsonify(errno=RET.AuthFailed, msg='token验证失败')
        except SignatureExpired:
            return jsonify(errno=RET.AuthFailed, msg='token过期')
        return jsonify(stat=RET.OK, msg="OK", data={"user_id": user_id, "name": name})
    else:
        return jsonify(errno=RET.AuthFailed, errmsg="Access-Token为空")


@api.route("/logout", methods=["DELETE"])
# @login_required
def logout():
    # 清除用户登录信息
    # session.pop("name", None)
    # session.pop("mobile", None)
    # session.pop("user_id", None)
    # user_id = g.user_id
    # try:
    #     redis_store.delete(f"token_{user_id}")
    # except Exception as e:
    #     current_app.logger.error(f"注销失败:"+e)
    #     return jsonify(errno=RET.SERVERERR, errmsg="ERR")
    return jsonify(stat=RET.OK, msg="OK")


@api.route("/login", methods=["POST"])
def login():
    # 1.获取参数
    data_dict = request.get_json()
    mobile = data_dict.get('username')
    password = data_dict.get('password')

    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 2.找到对应手机号的用户
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据错误')

    if not user:
        return jsonify(errno=RET.DATAERR, errmsg="用户不存在")

    # 3.校验密码
    if not user.check_password(password):
        return jsonify(errno=RET.PWDERR, errmsg="用户名或者密码错误")

    # # 4.保存登录状态返回结果
    # session['name'] = user.name
    # session['mobile'] = user.mobile
    # session['user_id'] = user.id


    # 5.返回结果
    token = s.dumps({"id": user.id, "mobile": user.mobile, "name": user.name}).decode('ascii')

    # 将token存入redis
    redis_store.set(f"token_{user.id}", token, LOGIN_REDIS_EXPIRES)

    res = dict(user.to_user_dict(), **{"token": token})
    return jsonify(stat=RET.OK, msg='登录成功', data=res)


@api.route('/register', methods=['POST'])
def register():
    '''
    :return:
    '''
    # 1.获取参数并判断是否有值
    data_dict = request.get_json()
    mobile = data_dict.get('mobile')
    name = data_dict.get('name')
    password = data_dict.get('password')

    if not all([mobile, name, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    # # 2.取到本地的验证码
    # try:
    #     sms_code = redis_store.get('SMS_' + mobile)
    #     redis_store.delete("SMS_" + mobile)
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.DBERR, errmsg='本地短信验证码获取失败')
    # if not sms_code:
    #     return jsonify(errno=RET.DBERR, errmsg='短信验证码过期')
    #
    # # 3.将本地验证码和传入的短信验证码进行对比，如果一样
    # if phonecode != sms_code:
    #     return jsonify(errno=RET.DATAERR, errmsg='短信验证码错误')

    # 4.创建用户模型，并设置数据，并添加到数据库
    user = User()
    # 设置数据
    user.name = name
    user.mobile = mobile
    user.password = password
    # 保存用户数据
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")

    # 保存登录状态
    # session['name'] = name
    # session['mobile'] = mobile
    # session['user_id'] = user.id
    token = s.dumps({"id": user.id, "mobile": user.mobile, "name": user.name}).decode('ascii')
    redis_store.set(f"token_{user.id}", token, LOGIN_REDIS_EXPIRES)
    res = dict(user.to_user_dict(), **{"token": token})

    # 5.返回结果
    return jsonify(stat=RET.OK, msg="注册成功", data=res)


@api.route('/user/info')
def retunUserInfo():
    permissions = {'permissions': ['test']}
    data = {
        "data": {
            "id": "4291d7da9005377ec9aec4a71ea837f",
            "name": "管理员",
            "username": "admin",
            "password": "",
            "avatar": "https://gw.alipayobjects.com/zos/rmsportal/jZUIxmJycoymBprLOUbT.png",
            "status": "1",
            "telephone": "",
            "lastLoginIp": "27.154.74.117",
            "lastLoginTime": "1534837621348",
            "creatorId": "admin",
            "createTime": "1497160610259",
            "merchantCode": "TLif2btpzg079h15bk",
            "deleted": "0",
            "roleList": [
                "admin",
                "company-admin"
            ],
            "funPermissionList": [
                "user_add",
                "user_delete"
            ],
            "role": permissions,
            "menuTree": [
                {
                    "path": "/welcome/index",
                    "flag": "welcome",
                    "title": "menu:welcome",
                    "icon": "smile"
                },
                {
                    "path": "/dashboard",
                    "flag": "dashboard",
                    "title": "menu:dashboard",
                    "icon": "eye",
                    "children": [
                        {
                            "path": "/dashboard/analysis",
                            "flag": "analysis",
                            "title": "menu:analysis"
                        },
                        {
                            "path": "https://www.baidu.com/",
                            "flag": "monitor",
                            "title": "menu:monitor"
                        },
                        {
                            "path": "/dashboard/workplac",
                            "flag": "workplac",
                            "title": "menu:workplac"
                        },
                        {
                            "path": "/other/test",
                            "flag": "test",
                            "title": "menu:test"
                        }
                    ]
                },
                {
                    "path": "/form",
                    "flag": "form",
                    "title": "menu:form",
                    "icon": "form",
                    "children": [
                        {
                            "path": "/form/base-form",
                            "flag": "BaseForm",
                            "title": "menu:BaseForm"
                        },
                        {
                            "path": "/form/step-form",
                            "flag": "StepForm",
                            "title": "menu:StepForm"
                        },
                        {
                            "path": "/form/advanced-form",
                            "flag": "AdvancedForm",
                            "title": "menu:AdvancedForm"
                        },
                        {
                            "path": "/form/other-form",
                            "flag": "OtherForm",
                            "title": "menu:OtherForm"
                        }
                    ]
                }
            ]
        },
    }
    return data


@api.route('/user/nav')
def retunUserNav():
    data = {
        "nav": {
            'name': 'testDemo',
            'parentId': 0,
            'id': 1,
            'meta': {
                'icon': 'dashboard',
                'title': '测试管理',
                'show': 'true'
            },
            'component': 'RouteView',
            'redirect': '/testDemo/test1'
        }
    }
    return data
