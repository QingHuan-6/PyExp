from flask import Blueprint

# 创建蓝图
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
data_bp = Blueprint('data', __name__, url_prefix='/api/data')
analysis_bp = Blueprint('analysis', __name__, url_prefix='/api/analysis')

# 导入路由视图
from app.routes import auth, data, analysis 