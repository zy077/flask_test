from . import index_blu
from flask import render_template, current_app, make_response
from flask_wtf.csrf import generate_csrf


# 给蓝图注册路由
@index_blu.route('/')
@index_blu.route("/index")
def index():
    # 1、生成csrf_token的值
    csrf_token = generate_csrf()
    # 2、渲染页面时，传入 csrf_token 到模板中
    resp = make_response(render_template('news/index.html', csrf_token=csrf_token))
    # 3、在cookie中设置csrf_token的值
    resp.set_cookie("csrf_token", csrf_token)
    return resp


@index_blu.route("/favicon.ico")
def favicon():
    return current_app.send_static_file('news/favicon.ico')  # send_static_file是系统访问静态文件所调用的方法
