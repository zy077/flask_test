from info.models import User, News, Category
from info.utils.response_code import RET
from . import index_blu
from flask import render_template, current_app, make_response, session, request, jsonify
from info import constants


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
        new_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
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


@index_blu.route('/news_list')
def get_news_list():
    """
    获取指定分类的新闻列表
    :return:
    """
    # 1、获取参数
    args_dict = request.args
    category_id = args_dict.get("cid", '1')
    page = args_dict.get("page", '1')
    per_page = args_dict.get("per_page", constants.HOME_PAGE_MAX_NEWS)  # 默认显示10条数据

    # 2、校验参数
    try:
        page = int(page)
        per_page = int(per_page)
        category_id = int(category_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({"errno": RET.PARAMERR, "errmsg": "参数错误"})

    # 3、查询数据并分页
    filter = []
    # 如果category_id不为1，则添加分类id过滤
    if category_id != 1:
        filter.append(News.category_id == category_id)

    try:
        paginate = News.query.filter(*filter).order_by(News.create_time.desc()).paginate(page, per_page, False)
        # 获取当前页的新闻数据
        items = paginate.items
        # 获取总页数
        total_page = paginate.pages
        # 获取当前页
        current_page = paginate.page
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({"errno": RET.DBERR, "errmsg": "查询数据错误！"})

    # 对查询到的数据做序列化处理
    news_list = []
    for new in items:
        news_list.append(new.to_basic_dict())

    data = {
        'totalPage': total_page,
        'current_page': current_page,
        'news_list': news_list,
        'cid': category_id
    }

    # 4、返回响应
    return jsonify(errno=RET.OK, errmsg="OK", data=data)
