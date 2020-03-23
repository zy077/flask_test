import random
import re

from flask import request, current_app, make_response, jsonify, Response, session
from flask_wtf import csrf

from info import redis_store, constants, db
from info.libs.yuntongxun.sms import CCP
from info.models import User
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET
from . import passport_blu


@passport_blu.route('/image_code')
def get_image_code():
    """
    获取图片验证码
    :return:
    """

    # 1、获取图片验证码id
    code_id = request.args.get("code_id")

    # 2、生成图片验证码
    name, text, image = captcha.generate_captcha()

    # 3、保存图片验证码
    try:
        redis_store.setex("ImageCode_" + code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify(errno=RET.DATAERR, errmsg="保存图片验证码失败"))

    # 4、返回验证码图片
    # resp = make_response(image)
    # # 设置响应类型
    # resp.headers["Content-Type"] = "image/jpg"
    # return resp
    print("图片验证码：%s" % text)
    return Response(image, content_type="image/jpg")


@passport_blu.route("/sms_code", methods=["GET", "POST"])
def send_sms():
    """
    发送短信验证码
    :return:
    """
    # 1、获取参数
    param_dict = request.args.to_dict()
    mobile = param_dict.get("mobile")
    image_code_id = param_dict.get("image_code_id")
    image_code = param_dict.get("image_code")

    # 判断该手机号是否已经注册
    user_num = User.query.filter_by(mobile=mobile).count()
    if user_num != 0:
        return jsonify(errno=RET.DATAEXIST, errmsg="该手机号已经被注册")

    # 2、校验参数
    # （1）参数是否齐全
    if not all([mobile, image_code_id, image_code]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # （2）手机号格式是否正确
    if not re.match(r"^1[3578][0-9]{9}$", mobile):
        return jsonify(errno=RET.DATAERR, errmsg="手机号格式不正确")

    # （3）图片验证码是否正确
    # 取出图片验证码
    try:
        real_image_code = redis_store.get("ImageCode_" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="获取图片验证码失败")
    # 判断图片验证码是否有效
    if real_image_code:
        real_image_code = real_image_code.decode()
        # 如果取到了图片验证码，删除redis中缓存的图片验证码，防止有人不断尝试
        redis_store.delete("ImageCode_" + image_code_id)
        # 判断图片验证码是否正确
        if real_image_code.lower() != image_code.lower():
            return jsonify(errno=RET.DATAERR, errmsg="图片验证码错误")
    else:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码已经过期")

    # 3、处理逻辑
    # （1）生成6位数的短信验证码
    sms_code = "%06d" % random.randint(0, 999999)

    # （2）发送短信验证码
    # ret = CCP.send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES/60], "1")
    # if ret != 0:
    #     return jsonify(errno=RET.THIRDERR, errmsg="发送短信验证码失败")
    print("短信验证码：%s" % sms_code)

    # （3）用redis保存短信验证码的内容
    try:
        redis_store.setex("SMS_" + mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存短信验证码失败")

    # 4、返回响应
    return jsonify(errno=RET.OK, errmsg="短信验证码发送成功")


@passport_blu.route('/register', methods=["GET", "POST"])
def register():
    """
    注册
    :return:
    """
    # 1、获取参数
    param_dict = request.json
    mobile = param_dict.get("mobile", "")
    smscode = param_dict.get("smscode", "")
    password = param_dict.get("password", "")

    # 2、检验
    # 参数是否齐全
    if not all([mobile, smscode, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")
    # 短信验证码是否正确
    try:
        real_sms_code = redis_store.get("SMS_" + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取本地短信验证码失败！")
    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码失效")
    if smscode != real_sms_code.decode():
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码错误")
    try:
        redis_store.delete("SMS_" + mobile)
    except Exception as e:
        current_app.logger.error(e)

    # 3、保存数据
    user = User()
    user.mobile = mobile
    user.nick_name = mobile
    # TODO hash_password，对密码加密处理
    hash_password = password
    user.password_hash = hash_password
    db.session.add(user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # 回滚
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="保存数据失败")

    # 保持用户登录状态
    session["user_id"] = user.id
    session["nick_name"] = user.nick_name
    session["mobile"] = user.mobile

    # 4、返回响应
    return jsonify(errno=RET.OK, errmsg="OK")
