from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app, db, models

# 创建app，传入配置模式：development / production
app = create_app("development")

# 集成flask_script，创建终端命令对象
manager = Manager(app)
# 使用数据库迁移类将应用和数据库连接对象关联起来
Migrate(app, db)
# 给终端命令对象添加数据库迁移命令
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
