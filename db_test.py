from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sys

# 从init.py导入app和db
try:
    from app.init import app, db
    print("成功从app.init导入app和db")
except ImportError as e:
    print(f"从app.init导入时出错: {e}")
    sys.exit(1)

def test_db_connection():
    try:
        # 尝试执行一个简单的查询
        result = db.engine.execute("SELECT 1")
        print("数据库连接成功！")
        return True
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return False

if __name__ == "__main__":
    with app.app_context():
        test_db_connection()
