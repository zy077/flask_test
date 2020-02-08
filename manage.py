from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app, db

# 创建app，传入配置模式：development / production
app = create_app("development")

# 集成flask_script，可以在命令行添加参数
manager = Manager(app)
# 数据库迁移
Migrate(app, db)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    app.run()
