from flask import current_app
import os

def allowed_file(filename):
    """检查文件是否为允许的类型"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def ensure_dir(directory):
    """确保目录存在，如不存在则创建"""
    if not os.path.exists(directory):
        os.makedirs(directory) 