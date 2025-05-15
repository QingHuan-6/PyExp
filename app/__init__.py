from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from config import config
from datetime import timedelta

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_name):
    app = Flask(__name__, static_folder='../static', static_url_path='/static')
    app.config.from_object(config[config_name])
    
    # 确保SECRET_KEY已设置
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = 'a-very-secret-key-please-change-in-production'
    
    # 关键: 设置会话配置
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
    app.config['SESSION_COOKIE_NAME'] = 'flask_session'
    app.config['SESSION_COOKIE_HTTPONLY'] = False
    app.config['SESSION_COOKIE_SECURE'] = False  # 开发环境
    app.config['SESSION_COOKIE_SAMESITE'] = None
    
    # 配置CORS，允许前端跨域请求
    CORS(app, 
         supports_credentials=True,
         resources={r"/api/*": {
             "origins": ["http://localhost:8080", "http://127.0.0.1:8080"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "X-User-ID", "Authorization"]
         }}
    )
    
    # 初始化插件
    db.init_app(app)
    migrate.init_app(app, db)
    
    # 特别注意login_manager的配置
    login_manager.init_app(app)
    login_manager.session_protection = None  # 开发时禁用，便于调试
    
    # 确保上传目录存在
    import os
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # 确保临时文件目录存在
    if not os.path.exists(app.config['TEMP_FOLDER']):
        os.makedirs(app.config['TEMP_FOLDER'])
    
    # 注册蓝图
    from app.routes import auth_bp, data_bp, analysis_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(data_bp)
    app.register_blueprint(analysis_bp)
    
    return app 