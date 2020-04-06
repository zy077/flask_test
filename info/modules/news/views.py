from flask import render_template, session, current_app, jsonify, g

from info.models import User, News
from info.utils.response_code import RET
from info import constants
from info.utils.common import user_login_data
from . import news_blu


@news_blu.route('/detail')
@user_login_data
def news_detail():
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

    data = {
        'user_info': g.user.to_dict() if g.user else None,  # 直接从g变量中获取登录用户的数据
        "click_news_list": click_news_list
    }

    return render_template('news/detail.html', data=data)
