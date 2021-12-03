# -*- coding: utf-8 -*-
# @Time    : 2021/12/2 10:14
# @Author  : WuBingTai

from ztest import db
from ztest.models import Phone, Borrow, User
from ztest.utils.common import login_required
from ztest.utils.response_code import RET
from ztest.utils.robot_push import push, robot_remind
from . import api
from flask import jsonify, request, current_app, g


# 借用列表
@api.route("/notReturned")
@login_required
def borrow_list():
    req = request.args
    page_size = int(req.get("page_size"))
    page = int(req.get("page"))

    params = list()
    if req.get('model'):
        params.append(Phone.model.like('%' + req.get('model') + '%'))
    if req.get('brand'):
        params.append(Phone.brand.like('%' + req.get('brand') + '%'))
    if req.get('name'):
        params.append(User.name.like('%' + req.get('name') + '%'))
    if req.get('administrative_number'):
        params.append(Phone.administrative_number == req.get('administrative_number'))

    if not all([page_size, page]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    try:
        paginate = db.session.query(Borrow, Phone, User).join(Phone, Borrow.borrow_phone_id == Phone.id).join(User,
                                                                                                              Borrow.borrow_user_id == User.id).filter(
            Borrow.create_time == Borrow.update_time).filter(*params).paginate(page, page_size, error_out=False)
        borrows = paginate.items
        pages = paginate.pages
        # has_prev = paginate.has_prev
        borrow_dict = []
        # print(borrows)
        for borrow in borrows:
            borrow_dict.append(
                dict(borrow[0].to_borrow_dict(), **borrow[1].to_phone_dict(), **borrow[2].to_user_dict()))
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")

    return jsonify(stat=RET.OK, msg="OK", data={"borrows": borrow_dict}, pages=pages)


# 我的借用列表
@api.route("/myBorrow")
@login_required
def my_borrow():
    req = request.args
    page_size = int(req.get("page_size"))
    page = int(req.get("page"))
    user_id = g.user_id

    if not all([page_size, page]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    try:
        paginate = db.session.query(Borrow, Phone).join(Phone, Borrow.borrow_phone_id == Phone.id).filter(
            Borrow.borrow_user_id == user_id, Borrow.create_time == Borrow.update_time).paginate(page, page_size,
                                                                                                 error_out=False)
        borrows = paginate.items
        pages = paginate.pages
        # has_prev = paginate.has_prev
        borrow_dict = []
        # print(borrows)
        for borrow in borrows:
            borrow_dict.append(dict(borrow[0].to_borrow_dict(), **borrow[1].to_phone_dict()))
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")

    return jsonify(stat=RET.OK, msg="OK", data={"borrows": borrow_dict}, pages=pages)


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


# 归还提醒
@api.route('/remind')
@login_required
def remind():
    idList = [1, 5, 7]
    if g.user_id in idList:
        robot_remind()
        return jsonify(stat=RET.OK, msg="操作成功")
    return jsonify(stat=RET.USERERR, msg="没有权限"), 403
