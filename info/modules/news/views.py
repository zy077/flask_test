from flask import render_template, session, current_app, jsonify, g, abort, request

from info.models import User, News
from info.utils.response_code import RET
from info import constants, db
from info.utils.common import user_login_data
from . import news_blu


@news_blu.route('/detail/<int:news_id>')
@user_login_data
def news_detail(news_id):
    """
    新闻详情
    :param news_id:
    :return:
    """
    # 获取登录用户的信息
    # user_id = session.get('user_id')
    #
    # user = None
    # if user_id:
    #     try:
    #         user = User.query.get(user_id)
    #     except Exception as e:
    #         current_app.logger.error(e)
    #         return jsonify({"errno": RET.DBERR, "errmsg": "查询数据失败！"})

    # 获取点击排行新闻信息
    # 1、获取新闻数据，按点击量从大到小排序
    try:
        click_news = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({"errno": RET.DBERR, "errmsg": "查询数据失败！"})

    # 2、序列化新闻数据
    click_news_list = []
    for news in click_news:
        click_news_list.append(news.to_dict())

    # 查询news_id的新闻
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({"errno": RET.DBERR, "errmsg": "查询数据失败！"})

    if not news:
        abort(404)

    # 添加变量is_collected，用于表示用户是否收藏了该新闻
    is_collected = False
    if g.user:
        if news in g.user.collection_news:
            is_collected = True

    data = {
        'user_info': g.user.to_dict() if g.user else None,  # 直接从g变量中获取登录用户的数据
        "click_news_list": click_news_list,
        "news": news.to_dict(),
        "is_collected": is_collected
    }
    return render_template('news/detail.html', data=data)


@news_blu.route('/collect', methods=['POST'])
@user_login_data
def news_collect():
    """
    收藏或者取消收藏
    :return:
    """
    # 用户必须登录，才能执行操作
    user = g.user
    if not user:
        return jsonify({'errno': RET.SESSIONERR, 'errmsg': '请先登录！'})

    # 1、获取参数
    params_dict = request.json
    news_id = params_dict.get('news_id')
    active = params_dict.get('action')

    # 2、校验参数
    if not all([news_id, active]):
        return jsonify({"errno": RET.PARAMERR, "errmsg": "参数不全"})
    if active not in ["collect", 'cancel_collect']:
        return jsonify({"errno": RET.PARAMERR, "errmsg": "参数错误"})

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({'errno': RET.DBERR, "errmsg": "查询数据失败！"})
    if not news:
        return jsonify({"errno": RET.NODATA, "errmsg": "数据不存在！"})

    # 3、更新用户收藏新闻数据
    if active == 'collect':
        # 收藏
        user.collection_news.append(news)
    else:
        # 取消收藏
        user.collection_news.remove(news)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify({"errno": RET.DBERR, "errmsg": "保存数据失败！"})

    # 4、返回响应
    return jsonify({"errno": RET.OK, "errmsg": "操作成功"})


