from flask import Flask
from config import config_dict
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
import logging
from logging.handlers import RotatingFileHandler
from flask_wtf.csrf import generate_csrf

# 数据库
db = SQLAlchemy()
redis_store = None

def setup_log(config_name):
    """配置日志"""

    # 设置日志的记录等级
    logging.basicConfig(level=config_dict[config_name].LOG_LEVEL)  # 调试DEBUG级
    # 设置日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存日志文件个数的上限
    file_log_handler = RotatingFileHandler(filename='logs/log', maxBytes=1024*1024*100, backupCount=10)
    # 创建日志记录的格式，日志等级、输入日志信息的文件名、行数、日志信息
    formatter = logging.Formatter("%(levelname)s %(filename)s:%(lineno)d %(message)s")
    # 为日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
    """根据传入不同的配置名字，初始化其对应配置的应用实例"""
    # 配置项目日志
    setup_log(config_name)

    app = Flask(__name__)

    # 加载配置
    app.config.from_object(config_dict[config_name])
    # 配置数据库
    db.init_app(app)
    # 配置redis
    global redis_store
    redis_store = redis.StrictRedis(host=config_dict[config_name].REDIS_HOST, port=config_dict[config_name].REDIS_PORT)
    # 开启CSRF保护
    CSRFProtect(app)
    # 设置session保存的位置
    Session(app)

    # 在执行完视图函数之后会调用，并且会把视图函数所生成的响应传入,可以在此方法中对响应做最后一步统一的处理
    @app.after_request
    def after_request(response):
        # 1、生成csrf_token的值
        csrf_token = generate_csrf()
        # 2、通过 cookie 将csrf_token的值传给前端
        response.set_cookie("csrf_token", csrf_token)
        return response

    # 添加过滤器
    from info.utils.common import do_index_class
    app.add_template_filter(do_index_class, 'index_class')

    # 把蓝图注册到app上
    from info.modules.index import index_blu
    app.register_blueprint(index_blu)
    from info.modules.passport import passport_blu
    app.register_blueprint(passport_blu)
    from info.modules.news import news_blu
    app.register_blueprint(news_blu)

    return app
