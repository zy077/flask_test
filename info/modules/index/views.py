from info.models import User, News, Category
from . import index_blu
from flask import render_template, current_app, make_response, session
from info.constants import CLICK_RANK_MAX_NEWS


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

    # 查询新闻数据，按点击量从大到小排行，只要前十条数据
    new_list = None
    try:
        # news = News.query.order_by('-clicks').limit(10)
        new_list = News.query.order_by(News.clicks.desc()).limit(CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    click_news_list = []
    for new in new_list if new_list else []:
        click_news_list.append(new.to_dict())

    # 查询新闻分类数据
    categories = Category.query.all()
    category_list = []
    # for category in enumerate(categories):
    for category in categories:
        category_list.append(category.to_dict())

    data = {
        "user_info": user.to_dict() if user else None,
        "click_news_list": click_news_list,
        "categories": category_list
    }
    return render_template('news/index.html', data=data)


@index_blu.route("/favicon.ico")
def favicon():
    return current_app.send_static_file('news/favicon.ico')  # send_static_file是系统访问静态文件所调用的方法
