from flask import request, jsonify, current_app, session
from flask_login import login_required, current_user
import os
import pandas as pd
import json
from werkzeug.utils import secure_filename
from app import db
from app.models.dataset import Dataset
from app.routes import data_bp
from app.services.data_cleaner import preview_data, clean_data
import numpy as np

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@data_bp.route('/upload', methods=['POST', 'OPTIONS'])
def upload_data_route():
    # 处理OPTIONS请求（预检请求）
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    print("上传文件API调用")
    print("请求头:", dict(request.headers))
    print("表单数据:", request.form)
    print("文件:", request.files)
    
    # 获取用户ID（使用多种方法尝试）
    user_id = None
    if current_user.is_authenticated:
        user_id = current_user.id
    elif 'user_id' in session:
        user_id = session['user_id']
    else:
        # 使用请求中的用户ID或默认ID
        user_id = request.form.get('user_id') or 1
    
    print(f"使用用户ID: {user_id}")
    
    # 检查是否有文件
    if 'file' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
        
    file = request.files['file']
    description = request.form.get('description', '')
    
    # 检查文件名
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
        
    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件类型'}), 400
    
    # 保存文件
    filename = secure_filename(file.filename)
    file_type = filename.rsplit('.', 1)[1].lower()
    
    # 创建用户目录
    user_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user_id))
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    
    # 生成唯一文件名
    import uuid
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    file_path = os.path.join(user_folder, unique_filename)
    file.save(file_path)
    
    try:
        # 读取数据信息
        preview_rows, total_rows, columns_info = preview_data(file_path, file_type)
        
        # 创建数据集记录
        dataset = Dataset(
            name=filename,
            description=description,
            file_path=file_path,
            file_type=file_type,
            user_id=user_id, 
            row_count=total_rows,
            columns=json.dumps(columns_info)
        )
        
        db.session.add(dataset)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '文件上传成功',
            'dataset': dataset.to_dict(),
            'preview': preview_rows
        })
        
    except Exception as e:
        # 删除上传的文件
        if os.path.exists(file_path):
            os.remove(file_path)
        print(f"处理文件错误: {str(e)}")
        return jsonify({'error': f'处理文件时出错: {str(e)}'}), 500

@data_bp.route('/preview', methods=['GET'])
def preview_data_route():
    # 简化实现，不调用实际函数
    return jsonify({'status': 'success', 'message': 'Data preview endpoint (not implemented)'})

@data_bp.route('/clean', methods=['POST'])
def clean_data_route():
    # 简化实现，不调用实际函数
    return jsonify({'status': 'success', 'message': 'Data cleaning endpoint (not implemented)'})

@data_bp.route('/datasets', methods=['GET', 'POST'])
def get_datasets():
    # 从请求中获取用户ID
    user_id_header = request.headers.get('X-User-ID')
    user_id_param = request.args.get('user_id')
    
    # 尝试多种方式获取用户ID
    user_id = None
    if current_user.is_authenticated:
        user_id = current_user.id
    elif user_id_header:
        user_id = int(user_id_header)
    elif user_id_param:
        user_id = int(user_id_param)
    elif 'user_id' in session:
        user_id = session['user_id']
    else:
        # 默认用户ID
        user_id = 1
    
    # 查询数据集
    try:
        datasets = Dataset.query.filter_by(user_id=user_id).all()
        return jsonify({'datasets': [d.to_dict() for d in datasets]})
    except Exception as e:
        print(f"查询错误: {e}")
        return jsonify({'datasets': []})

@data_bp.route('/datasets/<int:dataset_id>', methods=['GET'])
@login_required
def get_dataset(dataset_id):
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # 检查权限
    if dataset.user_id != current_user.id:
        return jsonify({'error': '无权访问该数据集'}), 403
    
    # 读取数据预览
    preview, _, _ = preview_data(dataset.file_path, dataset.file_type)

    return jsonify({
        'dataset': dataset.to_dict(),
        'preview': preview
    })

@data_bp.route('/datasets/<int:dataset_id>/clean', methods=['POST'])
@login_required
def clean_dataset(dataset_id):
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # 检查权限
    if dataset.user_id != current_user.id:
        return jsonify({'error': '无权访问该数据集'}), 403
    
    data = request.get_json()
    operations = data.get('operations', [])
    
    # 执行清洗操作
    result = clean_data(dataset.file_path, dataset.file_type, operations)
    
    if result['success']:
        # 更新数据集状态
        dataset.cleaned = True
        dataset.row_count = result['cleaned_count']
        
        # 确保列信息是JSON格式，与preview_data保持一致
        if 'columns' in result and isinstance(result['columns'], list):
            dataset.columns = json.dumps(result['columns'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '数据清洗成功',
            'preview': result['preview'],
            'original_count': result['original_count'],
            'cleaned_count': result['cleaned_count'],
            'removed_count': result['removed_count'],
            'column_count': result['column_count'],
            'added_column_count': result['added_column_count'],
            'columns': result.get('columns', [])
        })
    
    return jsonify({'error': result['error']}), 400

@data_bp.route('/datasets/<int:dataset_id>/clean-suggestions', methods=['GET'])
@login_required
def get_clean_suggestions(dataset_id):
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # 检查权限
    if dataset.user_id != current_user.id:
        return jsonify({'error': '无权访问该数据集'}), 403
    
    # 获取清洗建议
    result = auto_suggest_cleaning(dataset.file_path, dataset.file_type)
    
    if result['success']:
        return jsonify({
            'success': True,
            'suggestions': result['suggestions']
        })
    
    return jsonify({'error': result['error']}), 400

@data_bp.route('/datasets/<int:dataset_id>/apply-suggestion', methods=['POST'])
@login_required
def apply_clean_suggestion(dataset_id):
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # 检查权限
    if dataset.user_id != current_user.id:
        return jsonify({'error': '无权访问该数据集'}), 403
    
    data = request.get_json()
    suggestion = data.get('suggestion', {})
    
    # 将建议转换为操作
    operations = [suggestion]
    
    # 执行清洗操作
    result = clean_data(dataset.file_path, dataset.file_type, operations)
    
    if result['success']:
        # 更新数据集状态
        dataset.cleaned = True
        dataset.row_count = result['cleaned_count']
        
        # 确保列信息是JSON格式，与preview_data保持一致
        if 'columns' in result and isinstance(result['columns'], list):
            dataset.columns = json.dumps(result['columns'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '数据清洗成功',
            'preview': result['preview'],
            'original_count': result['original_count'],
            'cleaned_count': result['cleaned_count'],
            'removed_count': result['removed_count'],
            'column_count': result['column_count'],
            'added_column_count': result['added_column_count'],
            'columns': result.get('columns', [])
        })
    
    return jsonify({'success': False, 'error': result['error']}), 400

@data_bp.route('/datasets/<int:dataset_id>/full', methods=['GET'])
@login_required
def get_full_dataset(dataset_id):
    try:
        # 从数据库中获取数据集信息
        dataset = Dataset.query.get_or_404(dataset_id)
        
        # 检查权限
        if dataset.user_id != current_user.id:
            return jsonify({'success': False, 'error': '无权访问该数据集'}), 403
        
        # 检查文件是否存在
        if not os.path.exists(dataset.file_path):
            return jsonify({'success': False, 'error': f'找不到文件: {os.path.basename(dataset.file_path)}'}), 404
        
        # 根据文件类型读取文件
        file_type = dataset.file_type.lower()
        
        print(f"准备读取文件: {dataset.file_path}, 类型: {file_type}")
        
        # 读取整个文件
        if file_type == 'csv':
            df = pd.read_csv(dataset.file_path)
        elif file_type in ['xlsx', 'xls']:
            df = pd.read_excel(dataset.file_path)
        else:
            return jsonify({'success': False, 'error': f'不支持的文件类型: {file_type}'}), 400
        
        # 将NaN值替换为None，这样在JSON序列化时会变成null
        df = df.replace({np.nan: None})
        
        # 将DataFrame转换为字典列表
        records = df.to_dict(orient='records')
        
        # 记录一些基本信息，用于调试
        row_count = len(records)
        col_count = len(df.columns)
        
        print(f"成功读取文件，行数: {row_count}, 列数: {col_count}")
        
        # 返回结果
        return jsonify({
            'success': True,
            'data': records,
            'stats': {
                'row_count': row_count,
                'column_count': col_count
            }
        })
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        stack_trace = traceback.format_exc()
        print(f"读取文件时出错: {error_msg}")
        print(f"错误详情: {stack_trace}")
        return jsonify({'success': False, 'error': f'读取文件失败: {error_msg}'}), 500

def to_dict(self):
    return {
        'id': self.id,  # 确保这个字段存在
        'name': self.name,
        # 其他字段...
    } 