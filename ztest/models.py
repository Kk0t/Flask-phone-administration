# -*- coding: utf-8 -*-
# @Time    : 2021/9/8 10:56
# @Author  : WuBingTai
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, s


class BaseModel(object):
    """模型基类，为每个模型补充创建时间与更新时间"""

    create_time = db.Column(db.DateTime, default=datetime.now)  # 记录的创建时间
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 记录的更新时间


class User(BaseModel, db.Model):
    """用户"""

    __tablename__ = "user_profile"

    id = db.Column(db.Integer, primary_key=True)  # 用户编号
    name = db.Column(db.String(32), unique=True, nullable=False)  # 用户昵称
    password_hash = db.Column(db.String(128), nullable=False)  # 加密的密码
    mobile = db.Column(db.String(11), unique=True, nullable=False)  # 手机号
    real_name = db.Column(db.String(32))  # 真实姓名

    @property
    def password(self):
        raise AttributeError('属性不可读')

    @password.setter
    def password(self, pwd):
        """设置password的时候被调用，设置密码加密"""
        self.password_hash = generate_password_hash(pwd)

    def check_password(self, pwd):
        """提供校验密码的功能"""
        return check_password_hash(self.password_hash, pwd)

    def to_user_dict(self):
        user_dict = {
            "user_id": self.id,
            "mobile": self.mobile,
            "name": self.name

        }
        return user_dict

    @staticmethod
    def create_token(user_id, mobile, name):
        """
        :param user_id:
        :param mobile:
        :param name:
        :return:
        """
        token = s.dumps({"id": user_id, "mobile": mobile, "name": name}).decode('ascii')
        return token


class Borrow(BaseModel, db.Model):
    """借用记录"""
    __tablename__ = "borrow_info"

    id = db.Column(db.Integer, primary_key=True)
    borrow_user_id = db.Column(db.Integer, db.ForeignKey("user_profile.id"), nullable=False)
    borrow_phone_id = db.Column(db.Integer, db.ForeignKey("phone_info.id"), nullable=False)
    is_return = db.Column(  # 是否归还
        db.Enum(
            "1",  # 未归还,
            "0",  # 归还
        ),
        default="0", index=True
    )

    def to_borrow_dict(self):
        borrow_dict = {
            "borrow_id": self.id,
            "borrow_user_id": self.borrow_user_id,
            "borrow_phone_id": self.borrow_phone_id,
            "borrow_time": self.create_time.__str__(),
            "return_time": self.update_time.__str__()
        }
        return borrow_dict


class Phone(BaseModel, db.Model):
    """测试机"""
    __tablename__ = "phone_info"
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(32), nullable=False)  # 厂商
    model = db.Column(db.String(32), nullable=False)  # 型号
    os = db.Column(db.String(32), nullable=False)  # 系统
    pixel = db.Column(db.String(32), nullable=False)  # 像素
    cpu = db.Column(db.String(32), nullable=False)
    stat = db.Column(db.String(32))  # 状态
    ram = db.Column(db.String(32), nullable=False)
    screen_size = db.Column(db.String(32), nullable=False)  # 屏幕大小
    administrative_number = db.Column(db.String(32), unique=True, nullable=False)  # 行政编号
    colour = db.Column(db.String(32), nullable=False)  # 颜色
    remarks = db.Column(db.Text)  # 备注
    is_borrow = db.Column(  # 借用状态
        db.Enum(
            "1",  # 借用中,
            "0",  # 空闲
        ),
        default="0", index=True
    )

    # 获取手机列表
    def to_phone_dict(self):
        phone_dict = {
            "id": self.id,
            "brand": self.brand,
            "model": self.model,
            "os": self.os,
            "pixel": self.pixel,
            "cpu": self.cpu,
            "stat": self.stat,
            "ram": self.ram,
            "screen_size": self.screen_size,
            "administrative_number": self.administrative_number,
            "colour": self.colour,
            "remarks": self.remarks,
            "is_borrow": self.is_borrow
        }
        return phone_dict
