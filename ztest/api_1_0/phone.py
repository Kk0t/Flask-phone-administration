# -*- coding: utf-8 -*-
# @Time    : 2021/9/10 14:23
# @Author  : WuBingTai

from ztest import db
from ztest.models import Phone, Borrow
from ztest.utils.common import login_required
from ztest.utils.response_code import RET
from . import api
from ztest.utils.robot_push import push
from flask import jsonify, request, current_app, session, g


# 测试机列表
@api.route("/phone/list")
@login_required
def get_phone_list():

    req = request.args
    page_size = int(req.get("page_size"))
    page = int(req.get("page"))

    try:
        paginate = db.session.query(Phone).paginate(page, page_size, error_out=False)
        phones = paginate.items
        pages = paginate.pages
        # has_prev = paginate.has_prev
        phone_dict = []
        for phone in phones:
            phone_dict.append(phone.to_phone_dict())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")

    return jsonify(stat=RET.OK, msg="OK", data={"phones": phone_dict}, pages=pages)


# 新增手机
@api.route("/addPhone", methods=["POST"])
@login_required
def add_phone():
    data_dict = request.get_json()

    brand = data_dict.get("brand")
    model = data_dict.get("model")
    os = data_dict.get("os")
    pixel = data_dict.get("pixel")
    cpu = data_dict.get("cpu")
    ram = data_dict.get("ram")
    screen_size = data_dict.get("screen_size")
    administrative_number = data_dict.get("administrative_number")
    colour = data_dict.get("colour")

    if not all([brand, model, os, pixel, cpu, ram, screen_size, administrative_number, colour]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    phone = Phone()
    # 设置数据
    phone.brand = brand
    phone.model = model
    phone.os = os
    phone.cpu = cpu
    phone.pixel = pixel
    phone.ram = ram
    phone.screen_size = screen_size
    phone.administrative_number = administrative_number
    phone.colour = colour
    phone.is_borrow = "0"

    try:
        db.session.add(phone)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    return jsonify(stat=RET.OK, msg="添加成功", data=phone.to_phone_dict())


# 借用手机
@api.route("/borrowPhone", methods=["POST"])
@login_required
def borrow_phone():
    req = request.get_json()
    user_id = g.user_id
    phone_id = req.get("phone_id")

    if not phone_id:
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')
    phone = Phone.query.get(phone_id)
    if phone is None:
        return jsonify(errno=RET.DATAERR, errmsg='设备不存在')
    if phone.is_borrow == "1":
        return jsonify(errno=RET.UNKOWNERR, errmsg='设备借用中')

    borrow = Borrow()
    # 设置数据
    phone.is_borrow = "1"
    borrow.borrow_phone_id = phone_id
    borrow.borrow_user_id = user_id
    borrow.is_return = "0"
    try:
        db.session.add(borrow)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    push(g.user_name, 0, phone.brand + phone.model)  # push借用信息
    resp_dict = dict(borrow.to_borrow_dict(), **{"user_name": g.user_name})
    return jsonify(stat=RET.OK, msg="借用成功", data=resp_dict)


# 归还手机
@api.route("/returnPhone", methods=["POST"])
@login_required
def return_phone():
    req = request.get_json()
    borrow_id = req.get("borrow_id")
    user_id = g.user_id

    if not borrow_id:
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')
    borrow = Borrow.query.get(borrow_id)
    if borrow is None:
        return jsonify(errno=RET.DATAERR, errmsg='借用记录不存在')
    if borrow.borrow_user_id != user_id:
        return jsonify(errno=RET.USERERR, errmsg='借用人非当前用户')
    if borrow.is_return != "0":
        return jsonify(errno=RET.DATAERR, errmsg='设备已归还')

    phone = Phone.query.get(borrow.borrow_phone_id)
    phone.is_borrow = "0"
    borrow.is_return = "1"

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    push(g.user_name, 1, phone.brand + phone.model)  # push归还信息
    resp_dict = dict(borrow.to_borrow_dict(), **{"user_name": g.user_name})
    return jsonify(stat=RET.OK, msg="归还成功", data=resp_dict)
