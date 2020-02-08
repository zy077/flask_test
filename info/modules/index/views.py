from . import index_blu


# 给蓝图注册路由
@index_blu.route('/')
def index():
    return 'index'
