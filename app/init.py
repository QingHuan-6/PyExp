from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

# 初始化 Flask 应用
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/house_price'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 定义模型

class Dataset(db.Model):
    __tablename__ = 'datasets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    description = db.Column(db.Text)
    file_path = db.Column(db.String(256))  # 保存文件路径
    file_type = db.Column(db.String(16))   # csv, xlsx 等
    columns = db.Column(db.Text)  # 存储列信息的JSON字符串
    row_count = db.Column(db.Integer, default=0)
    cleaned = db.Column(db.Boolean, default=False)  # 是否已清洗
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    visualizations = db.relationship('Visualization', backref='dataset', lazy='dynamic')
    predictions = db.relationship('Prediction', backref='dataset', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'file_type': self.file_type,
            'columns': json.loads(self.columns) if self.columns else [],
            'row_count': self.row_count,
            'cleaned': self.cleaned,
            'created_at': self.created_at.isoformat(),
            'last_modified': self.last_modified.isoformat()
        }

class Visualization(db.Model):
    __tablename__ = 'visualizations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    chart_type = db.Column(db.String(32))  # bar, line, scatter, etc.
    config = db.Column(db.Text)  # JSON配置
    image_path = db.Column(db.String(256))  # 图像文件路径
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'))

class Prediction(db.Model):
    __tablename__ = 'predictions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    algorithm = db.Column(db.String(32))  # linear_regression, random_forest, etc.
    features = db.Column(db.Text)  # 使用的特征列表(JSON)
    target = db.Column(db.String(64))  # 目标列
    metrics = db.Column(db.Text)  # 评估指标(JSON)
    model_path = db.Column(db.String(256))  # 保存的模型路径
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'))

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    datasets = db.relationship('Dataset', backref='owner', lazy='dynamic')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

# 创建表的函数
def create_tables():
    with app.app_context():
        db.create_all()
    print("Tables created successfully!")

if __name__ == '__main__':
    create_tables()