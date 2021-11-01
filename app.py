# -*- coding: utf-8 -*-
# @Time    : 2021/9/7 16:45
# @Author  : WuBingTai
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from ztest import create_app, db

# 通过传入不同的配置名字，去创建不同配置的app
app = create_app("development")
manager = Manager(app)
# 集成数据库迁移
Migrate(app, db)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
