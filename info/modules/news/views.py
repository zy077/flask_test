from flask import render_template

from . import news_blu


@news_blu.route('/detail')
def news_detail():
    """
    新闻详情
    :param news_id:
    :return:
    """
    return render_template('news/detail.html')
