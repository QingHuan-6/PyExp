from flask import request, jsonify, current_app
from flask_login import login_required, current_user
import os
import json
from app import db
from app.models.dataset import Dataset, Visualization, Prediction
from app.routes import analysis_bp
from app.services.visualizer import create_visualization
from app.services.predictor import train_model, evaluate_model

@analysis_bp.route('/visualize/<int:dataset_id>', methods=['POST'])
@login_required
def visualize_data(dataset_id):
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # 检查权限
    if dataset.user_id != current_user.id:
        return jsonify({'error': '无权访问该数据集'}), 403
    
    data = request.get_json()
    chart_type = data.get('chart_type')
    config = data.get('config', {})
    name = data.get('name', f'{chart_type} chart')
    
    # 创建可视化
    result = create_visualization(dataset.file_path, dataset.file_type, chart_type, config)
    
    if result['success']:
        # 保存图表信息
        visualization = Visualization(
            name=name,
            chart_type=chart_type,
            config=json.dumps(config),
            image_path=result['image_path'],
            dataset_id=dataset_id
        )
        
        db.session.add(visualization)
        db.session.commit()
        
        return jsonify({
            'message': '可视化创建成功',
            'visualization_id': visualization.id,
            'image_url': f'/api/analysis/image/{visualization.id}'
        })
    
    return jsonify({'error': result['error']}), 400

@analysis_bp.route('/image/<int:visualization_id>')
@login_required
def get_visualization_image(visualization_id):
    visualization = Visualization.query.get_or_404(visualization_id)
    dataset = Dataset.query.get(visualization.dataset_id)
    
    # 检查权限
    if dataset.user_id != current_user.id:
        return jsonify({'error': '无权访问该可视化'}), 403
    
    # 返回图像文件
    from flask import send_file
    return send_file(visualization.image_path, mimetype='image/png')

@analysis_bp.route('/predict/<int:dataset_id>', methods=['POST'])
@login_required
def predict(dataset_id):
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # 检查权限
    if dataset.user_id != current_user.id:
        return jsonify({'error': '无权访问该数据集'}), 403
    
    data = request.get_json()
    algorithm = data.get('algorithm')
    features = data.get('features', [])
    target = data.get('target')
    name = data.get('name', f'{algorithm} model')
    
    # 训练模型
    result = train_model(dataset.file_path, dataset.file_type, algorithm, features, target)
    
    if result['success']:
        # 评估模型
        metrics = evaluate_model(result['model'], result['X_test'], result['y_test'])
        
        # 保存模型信息
        prediction = Prediction(
            name=name,
            algorithm=algorithm,
            features=json.dumps(features),
            target=target,
            metrics=json.dumps(metrics),
            model_path=result['model_path'],
            dataset_id=dataset_id
        )
        
        db.session.add(prediction)
        db.session.commit()
        
        return jsonify({
            'message': '模型训练成功',
            'prediction_id': prediction.id,
            'metrics': metrics
        })
    
    return jsonify({'error': result['error']}), 400

@analysis_bp.route('/predictions/<int:dataset_id>', methods=['GET'])
@login_required
def get_predictions(dataset_id):
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # 检查权限
    if dataset.user_id != current_user.id:
        return jsonify({'error': '无权访问该数据集'}), 403
    
    predictions = Prediction.query.filter_by(dataset_id=dataset_id).all()
    
    return jsonify({
        'predictions': [{
            'id': p.id,
            'name': p.name,
            'algorithm': p.algorithm,
            'features': json.loads(p.features),
            'target': p.target,
            'metrics': json.loads(p.metrics),
            'created_at': p.created_at.isoformat()
        } for p in predictions]
    })

@analysis_bp.route('/train', methods=['POST'])
def train_model_route():
    # 简化实现，不调用实际函数
    return jsonify({'status': 'success', 'message': 'Model training endpoint (not implemented)'})

@analysis_bp.route('/predict', methods=['POST'])
def predict_route():
    return jsonify({'status': 'success', 'message': 'Prediction endpoint (not implemented)'})

@analysis_bp.route('/evaluate', methods=['POST'])
def evaluate_model_route():
    # 简化实现，不调用实际函数
    return jsonify({'status': 'success', 'message': 'Model evaluation endpoint (not implemented)'}) 