from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
import logging
from logging.handlers import RotatingFileHandler

# 数据库
db = SQLAlchemy()
redis_store = None

def setup_log(config_name):
    """配置日志"""

    # 设置日志的记录等级
    logging.basicConfig(level=config[config_name].LOG_LEVEL)  # 调试DEBUG级
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
    app.config.from_object(config[config_name])
    # 配置数据库
    db.init_app(app)
    # 配置redis
    redis_store = redis.StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT)
    # 开启CSRF保护
    CSRFProtect(app)
    # 设置session保存的位置
    Session(app)

    # 把蓝图注册到app上
    from info.modules.index import index_blu
    app.register_blueprint(index_blu)

    return app
