from flask import request, current_app, make_response, jsonify, Response
from info import redis_store, constants
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
        return make_response(jsonify(errno=RET.DATAERR, errmag="保存图片验证码失败"))

    # 4、返回验证码图片
    # resp = make_response(image)
    # # 设置响应类型
    # resp.headers["Content-Type"] = "image/jpg"
    # return resp
    return Response(image, content_type="image/jpg")
