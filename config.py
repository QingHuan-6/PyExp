import os

class Config:
    # 应用配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    
    # 数据库配置 - 修改为MySQL
    # 格式: mysql+pymysql://username:password@host:port/database_name
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:123456@localhost:3306/house_price'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 上传文件配置
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # 临时文件配置
    TEMP_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'temp')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 