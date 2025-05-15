from app import create_app, db
from flask_migrate import Migrate
from sqlalchemy import text

app = create_app('default')

with app.app_context():
    # 使用SQL语句直接修改字段长度
    sql = text("ALTER TABLE users MODIFY password_hash VARCHAR(255)")
    db.session.execute(sql)
    db.session.commit()
    print("成功修改 password_hash 字段长度为 255") 