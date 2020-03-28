from info.models import User
from . import index_blu
from flask import render_template, current_app, make_response, session


# 给蓝图注册路由
@index_blu.route('/')
@index_blu.route("/index")
def index():
    # 判断用户是否登录
    user_id = session.get("user_id")
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        user = None

    # # 1、生成csrf_token的值
    # csrf_token = generate_csrf()
    # # 2、渲染页面时，传入 csrf_token 到模板中
    # resp = make_response(render_template('news/index.html', csrf_token=csrf_token, user_info=user.to_dict() if user else None))
    # # 3、在cookie中设置csrf_token的值
    # resp.set_cookie("csrf_token", csrf_token)
    # return resp

    return render_template('news/index.html', user_info=user.to_dict() if user else None)


@index_blu.route("/favicon.ico")
def favicon():
    return current_app.send_static_file('news/favicon.ico')  # send_static_file是系统访问静态文件所调用的方法
