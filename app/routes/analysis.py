from flask import request, jsonify, current_app,send_file
from flask_login import login_required, current_user
import os
import json
from app import db
from app.models.dataset import Dataset, Visualization, Prediction
from app.routes import analysis_bp
from app.services.visualizer import create_visualization
from app.services.predictor import train_model, evaluate_model
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
import joblib
# 导入房价预测模块
from app.services.predict_methods import load_data, preprocess_data, full_training_pipeline, predict, evaluate_model as evaluate_house_price_model
import time
import app.services.predict_methods

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
    
    # 获取图像路径并检查文件是否存在
    image_path = visualization.image_path
    if not os.path.exists(image_path):
        current_app.logger.error(f"找不到图像文件: {image_path}")
        return jsonify({'error': '找不到图像文件'}), 404
    
    # 返回图像文件
    try:
        from flask import send_file
        return send_file(image_path, mimetype='image/png')
    except Exception as e:
        current_app.logger.error(f"返回图像文件时出错: {str(e)}")
        return jsonify({'error': f'返回图像文件时出错: {str(e)}'}), 500

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

@analysis_bp.route('/perform_clustering', methods=['POST'])
@login_required
def api_perform_clustering():
    """API端点：执行聚类分析"""
    data = request.get_json()
    dataset_id = data.get('dataset_id')
    algorithm_config = data.get('algorithm_config', {})
    feature_columns = data.get('feature_columns', [])
    
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # 检查权限
    if dataset.user_id != current_user.id:
        return jsonify({'success': False, 'error': '无权访问该数据集'}), 403
    
    try:
        # 加载数据
        df = pd.read_csv(dataset.file_path)
        
        # 提取特征
        if not feature_columns:
            return jsonify({'success': False, 'error': '请选择至少一个特征列'}), 400
        
        features_df = df[feature_columns].dropna()
        
        # 检查并处理分类特征
        categorical_columns = []
        numerical_columns = []
        
        for column in features_df.columns:
            if features_df[column].dtype == 'object' or pd.api.types.is_categorical_dtype(features_df[column]):
                categorical_columns.append(column)
            else:
                numerical_columns.append(column)
        
        # 如果所有选择的特征都是分类型，返回错误
        if len(numerical_columns) == 0:
            return jsonify({
                'success': False, 
                'error': '请至少选择一个数值型特征进行聚类分析'
            }), 400
        
        # 如果存在分类特征，发送警告信息
        warning_message = None
        if categorical_columns:
            warning_message = f'已忽略以下分类特征: {", ".join(categorical_columns)}。聚类分析仅使用数值特征。'
            # 只使用数值特征
            features_df = features_df[numerical_columns]
        
        # 执行聚类
        result = perform_clustering(features_df, algorithm_config)
        
        # 保存结果
        tmp_file = os.path.join(current_app.config['TEMP_FOLDER'], f'cluster_{dataset_id}_{current_user.id}.joblib')
        joblib.dump(result, tmp_file)
        
        # 返回结果摘要
        if isinstance(result.get('labels'), np.ndarray):
            # 分析每个簇的大小
            unique_labels = np.unique(result['labels'])
            # 将numpy类型转换为Python原生类型
            cluster_sizes = [int(np.sum(result['labels'] == label)) for label in unique_labels]
            
            response = {
                'success': True,
                'cluster_count': int(len(unique_labels)),
                'cluster_sizes': cluster_sizes,
                'total_samples': int(len(result['labels'])),
                'outliers_count': int(np.sum(result['labels'] == -1)) if -1 in unique_labels else 0,
                'warning': warning_message
            }
        else:
            response = {
                'success': True,
                'message': '聚类完成，但无法解析簇信息',
                'warning': warning_message
            }
        
        return jsonify(response)
    
    except Exception as e:
        current_app.logger.error(f"聚类分析错误: {str(e)}")
        return jsonify({'success': False, 'error': f'聚类分析失败: {str(e)}'}), 500

@analysis_bp.route('/perform_classification', methods=['POST'])
@login_required
def api_perform_classification():
    """API端点：执行分类分析"""
    data = request.get_json()
    dataset_id = data.get('dataset_id')
    algorithm_config = data.get('algorithm_config', {})
    feature_columns = data.get('feature_columns', [])
    target_column = data.get('target_column')
    test_size = data.get('test_size', 0.2)
    
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # 检查权限
    if dataset.user_id != current_user.id:
        return jsonify({'success': False, 'error': '无权访问该数据集'}), 403
    
    try:
        # 参数验证
        if not feature_columns:
            return jsonify({'success': False, 'error': '请选择至少一个特征列'}), 400
        
        if not target_column:
            return jsonify({'success': False, 'error': '请选择目标列'}), 400
        
        # 加载数据
        df = pd.read_csv(dataset.file_path)
        
        # 提取特征和目标变量
        features_df = df[feature_columns].copy()
        
        # 检查并进行特征预处理
        categorical_columns = []
        for column in features_df.columns:
            if features_df[column].dtype == 'object' or pd.api.types.is_categorical_dtype(features_df[column]):
                categorical_columns.append(column)
        
        # 通过pandas的get_dummies进行分类特征编码
        if categorical_columns:
            # 仅对分类特征进行独热编码，保留数值特征
            # 创建一个临时数据框，避免警告
            encoded_features = pd.get_dummies(features_df, columns=categorical_columns, drop_first=True)
            features_df = encoded_features
        
        # 处理完成后进行特征选择，删除掉有缺失值的行
        features_df_clean = features_df.dropna()
        y = df[target_column].loc[features_df_clean.index]
        
        # 检查数据是否足够
        if len(features_df_clean) < 10:
            return jsonify({'success': False, 'error': '清理缺失值后的有效数据不足，请选择其他特征'}), 400
        
        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            features_df_clean, y, test_size=test_size, random_state=42
        )
        
        # 执行分类
        result = perform_classification(X_train, y_train, X_test, algorithm_config)
        result['y_test'] = y_test.values  # 添加真实标签用于评估
        
        # 保存结果
        tmp_file = os.path.join(current_app.config['TEMP_FOLDER'], f'classification_{dataset_id}_{current_user.id}.joblib')
        joblib.dump(result, tmp_file)
        
        # 计算基本指标
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        try:
            metrics = {
                'accuracy': float(accuracy_score(y_test, result['predictions'])),
                'samples': int(len(y_test))
            }
            
            # 对于二分类问题，计算更多指标
            if len(np.unique(y)) == 2:
                metrics.update({
                    'precision': float(precision_score(y_test, result['predictions'], average='binary')),
                    'recall': float(recall_score(y_test, result['predictions'], average='binary')),
                    'f1': float(f1_score(y_test, result['predictions'], average='binary'))
                })
                
            # 如果有分类特征，添加一个提示信息
            if categorical_columns:
                metrics['categorical_features_processed'] = True
                metrics['categorical_features'] = categorical_columns
        except Exception as e:
            metrics = {'error': str(e)}
        
        return jsonify({
            'success': True,
            'metrics': metrics
        })
    
    except Exception as e:
        current_app.logger.error(f"分类分析错误: {str(e)}")
        return jsonify({'success': False, 'error': f'分类分析失败: {str(e)}'}), 500

@analysis_bp.route('/perform_dimensionality_reduction', methods=['POST'])
@login_required
def api_perform_dimensionality_reduction():
    """API端点：执行降维分析"""
    data = request.get_json()
    dataset_id = data.get('dataset_id')
    algorithm_config = data.get('algorithm_config', {})
    feature_columns = data.get('feature_columns', [])
    
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # 检查权限
    if dataset.user_id != current_user.id:
        return jsonify({'success': False, 'error': '无权访问该数据集'}), 403
    
    try:
        # 参数验证
        if not feature_columns:
            return jsonify({'success': False, 'error': '请选择至少一个特征列'}), 400
        
        # 加载数据
        df = pd.read_csv(dataset.file_path)
        
        # 提取特征
        features_df = df[feature_columns].dropna()
        
        # 检查并处理分类特征
        categorical_columns = []
        numerical_columns = []
        
        for column in features_df.columns:
            if features_df[column].dtype == 'object' or pd.api.types.is_categorical_dtype(features_df[column]):
                categorical_columns.append(column)
            else:
                numerical_columns.append(column)
        
        # 如果所有选择的特征都是分类型，返回错误
        if len(numerical_columns) == 0:
            return jsonify({
                'success': False, 
                'error': '请至少选择一个数值型特征进行降维分析'
            }), 400
        
        # 如果存在分类特征，发送警告信息
        warning_message = None
        if categorical_columns:
            warning_message = f'已忽略以下分类特征: {", ".join(categorical_columns)}。降维分析仅使用数值特征。'
            # 只使用数值特征
            features_df = features_df[numerical_columns]
        
        # 执行降维
        result = perform_dimensionality_reduction(features_df, algorithm_config)
        
        # 保存结果
        tmp_file = os.path.join(current_app.config['TEMP_FOLDER'], f'reduction_{dataset_id}_{current_user.id}.joblib')
        joblib.dump(result, tmp_file)
        
        # 为了前端可视化，返回降维后的前两个维度数据
        if isinstance(result.get('transformed_data'), np.ndarray):
            # 仅返回前1000个点以避免数据过大
            data_sample = result['transformed_data'][:1000]
            if data_sample.shape[1] >= 2:
                data_2d = data_sample[:, :2].tolist()
            else:
                data_2d = data_sample.tolist()
            
            response = {
                'success': True,
                'data_2d': data_2d,
                'total_samples': int(len(result['transformed_data'])),
                'returned_samples': int(len(data_2d)),
                'explained_variance': result.get('explained_variance', None),
                'warning': warning_message
            }
        else:
            response = {
                'success': True,
                'message': '降维完成，但无法提取可视化数据',
                'warning': warning_message
            }
        
        return jsonify(response)
    
    except Exception as e:
        current_app.logger.error(f"降维分析错误: {str(e)}")
        return jsonify({'success': False, 'error': f'降维分析失败: {str(e)}'}), 500

@analysis_bp.route('/train_price_model', methods=['POST'])
@login_required
def train_price_model():
    """训练房价预测模型的API端点"""
    try:
        data = request.get_json()
        dataset_id = data.get('dataset_id')
        model_name = data.get('model_name', '房价预测模型')
        
        # 获取数据集
        dataset = Dataset.query.get_or_404(dataset_id)
        
        # 检查权限
        if dataset.user_id != current_user.id:
            return jsonify({'success': False, 'error': '无权访问该数据集'}), 403
        
        # 设置模型和预处理器保存路径
        model_filename = f'house_price_model_{dataset_id}_{current_user.id}.joblib'
        preprocessor_filename = f'house_price_preprocessor_{dataset_id}_{current_user.id}.joblib'
        
        model_path = os.path.join(current_app.config['TEMP_FOLDER'], model_filename)
        preprocessor_path = os.path.join(current_app.config['TEMP_FOLDER'], preprocessor_filename)
        
        # 确保临时目录存在
        os.makedirs(current_app.config['TEMP_FOLDER'], exist_ok=True)
        
        # 执行完整训练流程
        model, preprocessor_objects = full_training_pipeline(
            train_file_path=dataset.file_path,
            model_save_path=model_path,
            preprocessor_save_path=preprocessor_path
        )
        
        # 加载数据用于评估
        df = load_data(dataset.file_path)
        
        # 提取特征和标签
        features, target, _, _ = preprocess_data(df, training=True)
        
        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            features, target, test_size=0.2, random_state=42
        )
        
        # 评估模型
        metrics = evaluate_house_price_model(model, X_test, y_test)
        
        # 保存模型信息到数据库
        prediction = Prediction(
            name=model_name,
            algorithm='xgboost',  # 固定使用XGBoost算法
            features=json.dumps(preprocessor_objects.get('feature_names', [])),
            target='SalePrice',  # 固定目标变量
            metrics=json.dumps(metrics),
            model_path=model_path,
            dataset_id=dataset_id,
            preprocessor_path=preprocessor_path  # 新增字段，存储预处理器路径
        )
        
        db.session.add(prediction)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '房价预测模型训练成功',
            'prediction_id': prediction.id,
            'metrics': metrics
        })
        
    except Exception as e:
        current_app.logger.error(f"训练房价预测模型出错: {str(e)}")
        return jsonify({
            'success': False, 
            'error': f'训练模型失败: {str(e)}'
        }), 500

@analysis_bp.route('/predict_house_price', methods=['POST'])
@login_required
def predict_house_price():
    """使用训练好的模型预测房价"""
    try:
        # 确保请求包含文件
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '没有上传文件'}), 400
        
        file = request.files['file']
        
        # 检查文件名是否为空
        if file.filename == '':
            return jsonify({'success': False, 'error': '没有选择文件'}), 400
        
        # 检查是否为CSV文件
        if not file.filename.endswith('.csv'):
            return jsonify({'success': False, 'error': '只支持CSV文件'}), 400
        
        # 获取预测模型ID
        prediction_id = request.form.get('prediction_id')
        if not prediction_id:
            return jsonify({'success': False, 'error': '未提供模型ID'}), 400
        
        # 获取模型信息
        prediction_model = Prediction.query.get_or_404(prediction_id)
        
        # 检查权限
        if prediction_model.dataset.user_id != current_user.id:
            return jsonify({'success': False, 'error': '无权访问该模型'}), 403
        
        # 检查模型和预处理器路径是否存在
        if not prediction_model.model_path or not prediction_model.preprocessor_path:
            return jsonify({'success': False, 'error': '模型信息不完整'}), 400
        
        # 保存上传的文件
        temp_folder = current_app.config['TEMP_FOLDER']
        os.makedirs(temp_folder, exist_ok=True)
        
        test_file_path = os.path.join(temp_folder, f'test_file_{current_user.id}_{int(time.time())}.csv')
        file.save(test_file_path)
        
        # 加载测试数据集
        test_data = load_data(test_file_path)
        
        # 进行预测
        predictions, id_column = app.services.predict_methods.predict(
            test_data,
            prediction_model.model_path,
            prediction_model.preprocessor_path
        )
        
        # 创建预测结果列表
        prediction_results = []
        for i in range(len(predictions)):
            row_id = int(id_column[i]) if id_column is not None else i + 1
            prediction_results.append({
                'id': row_id,
                'predicted_price': float(predictions[i])
            })
        
        # 计算一些汇总统计信息
        summary = {
            'count': len(predictions),
            'mean': float(np.mean(predictions)),
            'median': float(np.median(predictions)),
            'min': float(np.min(predictions)),
            'max': float(np.max(predictions))
        }
        
        # 清理临时文件
        try:
            os.remove(test_file_path)
        except:
            current_app.logger.warning(f"无法删除临时文件: {test_file_path}")
        
        return jsonify({
            'success': True,
            'message': '房价预测完成',
            'predictions': prediction_results[:100],  # 仅返回前100个结果避免响应过大
            'total_predictions': len(predictions),
            'summary': summary
        })
        
    except Exception as e:
        current_app.logger.error(f"预测房价出错: {str(e)}")
        return jsonify({
            'success': False, 
            'error': f'预测失败: {str(e)}'
        }), 500

def perform_clustering(data, algorithm_config):
    """
    执行聚类分析
    
    参数:
        data: pandas.DataFrame 或 numpy.ndarray
        algorithm_config: 字典，包含算法类型和参数
    
    返回:
        包含聚类结果的字典
    """
    algorithm = algorithm_config.get('algorithm', 'kmeans').lower()
    params = algorithm_config.get('params', {})
    
    # 确保数据是numpy数组
    if isinstance(data, pd.DataFrame):
        features = data.values
    else:
        features = data
    
    result = {'algorithm': algorithm}
    
    if algorithm == 'kmeans':
        # 设置默认参数，并覆盖用户提供的参数
        n_clusters = params.get('n_clusters', 3)
        init = params.get('init', 'k-means++')
        n_init = params.get('n_init', 10)
        max_iter = params.get('max_iter', 300)
        random_state = params.get('random_state', 42)
        
        # 执行K-means聚类
        kmeans = KMeans(
            n_clusters=n_clusters,
            init=init,
            n_init=n_init,
            max_iter=max_iter,
            random_state=random_state
        )
        
        labels = kmeans.fit_predict(features)
        
        # 保存结果
        result.update({
            'labels': labels,
            'model': kmeans,
            'inertia': kmeans.inertia_,
            'centers': kmeans.cluster_centers_
        })
    
    elif algorithm == 'dbscan':
        # 设置默认参数
        eps = params.get('eps', 0.5)
        min_samples = params.get('min_samples', 5)
        
        # 执行DBSCAN聚类
        dbscan = DBSCAN(
            eps=eps,
            min_samples=min_samples
        )
        
        labels = dbscan.fit_predict(features)
        
        # 保存结果
        result.update({
            'labels': labels,
            'model': dbscan,
            'n_clusters': len(set(labels)) - (1 if -1 in labels else 0)  # 不包括噪声点
        })
    
    elif algorithm == 'hierarchical':
        # 设置默认参数
        n_clusters = params.get('n_clusters', 3)
        linkage = params.get('linkage', 'ward')
        
        # 执行层次聚类
        hc = AgglomerativeClustering(
            n_clusters=n_clusters,
            linkage=linkage
        )
        
        labels = hc.fit_predict(features)
        
        # 保存结果
        result.update({
            'labels': labels,
            'model': hc,
            'n_clusters': n_clusters
        })
    
    else:
        raise ValueError(f"不支持的聚类算法: {algorithm}")
    
    return result

def perform_classification(X_train, y_train, X_test, algorithm_config):
    """
    执行分类分析
    
    参数:
        X_train: 训练集特征
        y_train: 训练集标签
        X_test: 测试集特征
        algorithm_config: 字典，包含算法类型和参数
    
    返回:
        包含分类结果的字典
    """
    algorithm = algorithm_config.get('algorithm', 'logistic_regression').lower()
    params = algorithm_config.get('params', {})
    
    # 确保数据是numpy数组
    if isinstance(X_train, pd.DataFrame):
        X_train = X_train.values
    if isinstance(y_train, pd.Series):
        y_train = y_train.values
    if isinstance(X_test, pd.DataFrame):
        X_test = X_test.values
    
    result = {'algorithm': algorithm}
    
    if algorithm == 'logistic_regression':
        # 设置默认参数
        penalty = params.get('penalty', 'l2')
        C = params.get('C', 1.0)
        solver = params.get('solver', 'liblinear')
        max_iter = params.get('max_iter', 100)
        random_state = params.get('random_state', 42)
        
        # 执行逻辑回归
        clf = LogisticRegression(
            penalty=penalty,
            C=C,
            solver=solver,
            max_iter=max_iter,
            random_state=random_state
        )
        
        clf.fit(X_train, y_train)
        predictions = clf.predict(X_test)
        
        # 保存结果
        result.update({
            'model': clf,
            'predictions': predictions,
            'probabilities': clf.predict_proba(X_test) if hasattr(clf, 'predict_proba') else None
        })
    
    elif algorithm == 'random_forest':
        # 设置默认参数
        n_estimators = params.get('n_estimators', 100)
        max_depth = params.get('max_depth', None)
        min_samples_split = params.get('min_samples_split', 2)
        random_state = params.get('random_state', 42)
        
        # 执行随机森林分类
        clf = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            random_state=random_state
        )
        
        clf.fit(X_train, y_train)
        predictions = clf.predict(X_test)
        
        # 保存结果
        result.update({
            'model': clf,
            'predictions': predictions,
            'feature_importances': clf.feature_importances_,
            'probabilities': clf.predict_proba(X_test) if hasattr(clf, 'predict_proba') else None
        })
    
    elif algorithm == 'svm':
        # 设置默认参数
        C = params.get('C', 1.0)
        kernel = params.get('kernel', 'rbf')
        gamma = params.get('gamma', 'scale')
        
        # 执行SVM分类
        clf = SVC(
            C=C,
            kernel=kernel,
            gamma=gamma,
            probability=True
        )
        
        clf.fit(X_train, y_train)
        predictions = clf.predict(X_test)
        
        # 保存结果
        result.update({
            'model': clf,
            'predictions': predictions,
            'probabilities': clf.predict_proba(X_test) if hasattr(clf, 'predict_proba') else None
        })
    
    else:
        raise ValueError(f"不支持的分类算法: {algorithm}")
    
    return result

def perform_dimensionality_reduction(data, algorithm_config):
    """
    执行降维分析
    
    参数:
        data: pandas.DataFrame 或 numpy.ndarray
        algorithm_config: 字典，包含算法类型和参数
    
    返回:
        包含降维结果的字典
    """
    algorithm = algorithm_config.get('algorithm', 'pca').lower()
    params = algorithm_config.get('params', {})
    
    # 确保数据是numpy数组
    if isinstance(data, pd.DataFrame):
        features = data.values
    else:
        features = data
    
    result = {'algorithm': algorithm}
    
    if algorithm == 'pca':
        # 设置默认参数
        n_components = params.get('n_components', 2)
        svd_solver = params.get('svd_solver', 'auto')
        random_state = params.get('random_state', 42)
        
        # 执行PCA降维
        pca = PCA(
            n_components=n_components,
            svd_solver=svd_solver,
            random_state=random_state
        )
        
        transformed_data = pca.fit_transform(features)
        
        # 保存结果
        result.update({
            'model': pca,
            'transformed_data': transformed_data,
            'components': pca.components_,
            'explained_variance': pca.explained_variance_ratio_.tolist() if hasattr(pca, 'explained_variance_ratio_') else None
        })
    
    elif algorithm == 'tsne':
        # 设置默认参数
        n_components = params.get('n_components', 2)
        perplexity = params.get('perplexity', 30.0)
        learning_rate = params.get('learning_rate', 'auto')
        n_iter = params.get('n_iter', 1000)
        random_state = params.get('random_state', 42)
        
        # 执行t-SNE降维
        tsne = TSNE(
            n_components=n_components,
            perplexity=perplexity,
            learning_rate=learning_rate,
            n_iter=n_iter,
            random_state=random_state
        )
        
        transformed_data = tsne.fit_transform(features)
        
        # 保存结果
        result.update({
            'model': tsne,
            'transformed_data': transformed_data
        })
    
    else:
        raise ValueError(f"不支持的降维算法: {algorithm}")
    
    return result 