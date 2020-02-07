from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session

# 数据库
db = SQLAlchemy()
redis_store = None


def create_app(config_name):
    """根据传入不同的配置名字，初始化其对应配置的应用实例"""
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

    return app
