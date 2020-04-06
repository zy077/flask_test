import functools

from flask import session, current_app, g

from info.models import User


def do_index_class(index):
    """自定义过滤器，过滤点击排行html的class"""
    if index == 1:
        return 'first'
    elif index == 2:
        return 'second'
    elif index == 3:
        return 'third'
    else:
        return ''


def user_login_data(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 在执行被装饰函数前加载用户数据，并保存到g变量中
        user_id = session.get('user_id')

        user = None
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

        # 保存用户数据
        g.user = user

        return func(*args, **kwargs)

    return wrapper


