# -*- coding: utf-8 -*-
# @Time    : 2021/9/10 14:23
# @Author  : WuBingTai

from ztest import db
from ztest.models import Phone
from ztest.utils.common import login_required
from ztest.utils.response_code import RET
from . import api
from flask import jsonify, request, current_app


# 测试机列表
@api.route("/phone/list")
@login_required
def get_phone_list():
    req = request.args
    page_size = int(req.get("page_size"))
    page = int(req.get("page"))

    params = list()
    if req.get('model'):
        params.append(Phone.model.like('%' + req.get('model') + '%'))
    if req.get('brand'):
        params.append(Phone.brand.like('%' + req.get('brand') + '%'))
    if req.get('os'):
        params.append(Phone.os.like('%' + req.get('os') + '%'))
    if req.get('pixel'):
        params.append(Phone.pixel.like('%' + req.get('pixel') + '%'))
    if req.get('is_borrow'):
        params.append(Phone.is_borrow == req.get('is_borrow'))
    if req.get('administrative_number'):
        params.append(Phone.administrative_number == req.get('administrative_number'))

    try:
        paginate = db.session.query(Phone).filter(*params).paginate(page, page_size, error_out=False)
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
    data_dict = request.form

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
