from flask import request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models.user import User
from app.routes import auth_bp

@auth_bp.route('/register', methods=['POST'])
def register():
    # 获取请求数据
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '无效的请求数据'}), 400
        
    # 提取必要信息
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    # 验证必填字段
    if not username or not email or not password:
        return jsonify({'error': '用户名、邮箱和密码不能为空'}), 400
    
    # 检查用户名和邮箱是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'error': '用户名已被使用'}), 400
        
    if User.query.filter_by(email=email).first():
        return jsonify({'error': '邮箱已被注册'}), 400
    
    # 创建新用户
    new_user = User(
        username=username,
        email=email, 
        password=password  # User模型中的__init__会处理密码哈希
    )
    
    # 保存到数据库
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '注册成功，请登录'
    })

@auth_bp.route('/login', methods=['POST'])
def login():
    # 获取请求数据
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '无效的请求数据'}), 400
    
    # 提取登录信息
    username_or_email = data.get('username')
    password = data.get('password')
    
    # 验证必填字段
    if not username_or_email or not password:
        return jsonify({'error': '用户名/邮箱和密码不能为空'}), 400
    
    # 查询用户
    user = User.query.filter((User.username == username_or_email) | 
                           (User.email == username_or_email)).first()
    
    # 检查用户是否存在及密码是否正确
    if user is None or not user.check_password(password):
        return jsonify({'error': '用户名/邮箱或密码不正确'}), 401
    
    # 关键：强制创建新的会话
    if '_flashes' in session:
        del session['_flashes']
    
    # 确保登录状态正确
    login_user(user, remember=True)
    
    # 手动设置会话数据以强制会话更新
    session['user_id'] = user.id
    session['logged_in'] = True
    session.permanent = True
    
    print(f"用户 {user.username} 登录成功")
    print(f"is_authenticated = {current_user.is_authenticated}")
    print(f"会话数据: {session}")
    
    # 设置一个明确的响应，包含必要的cookie设置
    response = jsonify({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        },
        'debug': {
            'authenticated': current_user.is_authenticated,
            'user_id': session.get('user_id'),
            'session_id': session.get('_id', 'unknown')
        }
    })
    
    return response

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    # 移除@login_required装饰器，防止未认证用户无法访问
    # 即使用户未登录也返回成功
    try:
        logout_user()
    except:
        pass
    
    return jsonify({
        'success': True,
        'message': '已登出'
    })

@auth_bp.route('/user')
@login_required
def get_user():
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email
    }) 