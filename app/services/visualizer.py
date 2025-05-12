import pandas as pd
import os
import uuid
from app.services.data_cleaner import read_file
from flask import current_app

# 明确设置matplotlib使用非交互式后端，必须在导入pyplot之前设置
import matplotlib
matplotlib.use('Agg')  # 使用Agg后端，适合服务器端生成图像
import matplotlib.pyplot as plt
import seaborn as sns

def create_visualization(file_path, file_type, chart_type, config):
    """根据配置创建可视化图表"""
    try:
        # 读取数据
        df = read_file(file_path, file_type)
        
        # 处理无穷值
        # 替换掉可能的inf值，这比使用已弃用的mode.use_inf_as_null更好
        df = df.replace([float('inf'), -float('inf')], pd.NA)
        
        # 设置图表风格
        sns.set_theme(style="whitegrid")
        plt.figure(figsize=(10, 6))
        
        # 根据图表类型绘制不同的图
        if chart_type == 'bar':
            x = config.get('x')
            y = config.get('y')
            hue = config.get('hue')
            
            if not x or not y:
                return {'success': False, 'error': '缺少必要的参数: x和y'}
            
            if hue:
                sns.barplot(data=df, x=x, y=y, hue=hue)
            else:
                sns.barplot(data=df, x=x, y=y)
            
            plt.title(config.get('title', f'Bar Chart - {y} by {x}'))
            
        elif chart_type == 'line':
            x = config.get('x')
            y = config.get('y')
            hue = config.get('hue')
            
            if not x or not y:
                return {'success': False, 'error': '缺少必要的参数: x和y'}
            
            # 确保line图的数据没有NaN值
            line_df = df[[x, y]].dropna()
            
            if hue:
                if hue in df.columns:
                    line_df = df[[x, y, hue]].dropna()
                    sns.lineplot(data=line_df, x=x, y=y, hue=hue)
                else:
                    sns.lineplot(data=line_df, x=x, y=y)
            else:
                sns.lineplot(data=line_df, x=x, y=y)
            
            plt.title(config.get('title', f'Line Chart - {y} over {x}'))
            
        elif chart_type == 'scatter':
            x = config.get('x')
            y = config.get('y')
            hue = config.get('hue')
            
            if not x or not y:
                return {'success': False, 'error': '缺少必要的参数: x和y'}
            
            # 过滤掉NaN值
            scatter_df = df[[x, y]].dropna()
            
            if hue:
                if hue in df.columns:
                    scatter_df = df[[x, y, hue]].dropna()
                    sns.scatterplot(data=scatter_df, x=x, y=y, hue=hue)
                else:
                    sns.scatterplot(data=scatter_df, x=x, y=y)
            else:
                sns.scatterplot(data=scatter_df, x=x, y=y)
            
            plt.title(config.get('title', f'Scatter Plot - {y} vs {x}'))
            
        elif chart_type == 'histogram':
            x = config.get('x')
            bins = config.get('bins', 10)
            
            if not x:
                return {'success': False, 'error': '缺少必要的参数: x'}
            
            # 过滤掉NaN值
            hist_df = df[[x]].dropna()
            
            sns.histplot(data=hist_df, x=x, bins=bins)
            plt.title(config.get('title', f'Histogram of {x}'))
            
        elif chart_type == 'heatmap':
            columns = config.get('columns', [])
            
            if not columns or len(columns) < 2:
                return {'success': False, 'error': '需要至少两列进行热图分析'}
            
            # 确保所选列存在
            valid_columns = [col for col in columns if col in df.columns]
            if len(valid_columns) < 2:
                return {'success': False, 'error': '选择的列不存在于数据集中'}
                
            # 计算相关性，处理NaN值
            corr = df[valid_columns].corr()
            sns.heatmap(corr, annot=True, cmap='coolwarm')
            plt.title(config.get('title', 'Correlation Heatmap'))
            
        elif chart_type == 'box':
            x = config.get('x')
            y = config.get('y')
            
            if not y:
                return {'success': False, 'error': '缺少必要的参数: y'}
            
            # 过滤掉y列中的NaN值
            box_df = df[[y]].dropna()
            
            if x and x in df.columns:
                box_df = df[[x, y]].dropna()
                sns.boxplot(data=box_df, x=x, y=y)
            else:
                sns.boxplot(data=box_df, y=y)
            
            plt.title(config.get('title', f'Box Plot of {y}'))
            
        else:
            return {'success': False, 'error': f'不支持的图表类型: {chart_type}'}
        
        # 保存图表到项目根目录的static/images文件夹
        # 获取应用的根目录
        app_root = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        image_dir = os.path.join(app_root, 'static', 'images')
        
        # 确保目录存在
        os.makedirs(image_dir, exist_ok=True)
            
        filename = f"{chart_type}_{uuid.uuid4().hex}.png"
        image_path = os.path.join(image_dir, filename)
        
        plt.tight_layout()
        plt.savefig(image_path)
        plt.close('all')  # 关闭所有figure，释放资源
        
        # 明确触发Python的垃圾回收
        import gc
        gc.collect()
        
        return {
            'success': True,
            'image_path': image_path
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        # 确保清理任何打开的图像
        plt.close('all')
        
        return {
            'success': False,
            'error': str(e)
        }

def create_cluster_visualization(file_path, file_type, config):
    """创建聚类分析可视化图表"""
    try:
        # 读取数据
        df = read_file(file_path, file_type)
        
        # 处理无穷值
        df = df.replace([float('inf'), -float('inf')], pd.NA)
        
        # 获取配置参数
        features = config.get('features', [])
        n_clusters = config.get('n_clusters', 3)
        algorithm = config.get('algorithm', 'kmeans')
        
        if not features or len(features) < 2:
            return {'success': False, 'error': '聚类分析至少需要选择两个特征'}
        
        # 确保所选特征存在于数据集中
        valid_features = [col for col in features if col in df.columns]
        if len(valid_features) < 2:
            return {'success': False, 'error': '选择的特征不存在于数据集中'}
        
        # 选择特征并删除缺失值
        X = df[valid_features].dropna()
        
        # 标准化数据
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # 根据算法进行聚类
        labels = None
        if algorithm == 'kmeans':
            from sklearn.cluster import KMeans
            model = KMeans(n_clusters=n_clusters, random_state=42)
            labels = model.fit_predict(X_scaled)
        elif algorithm == 'dbscan':
            from sklearn.cluster import DBSCAN
            eps = config.get('eps', 0.5)
            min_samples = config.get('min_samples', 5)
            model = DBSCAN(eps=eps, min_samples=min_samples)
            labels = model.fit_predict(X_scaled)
        elif algorithm == 'hierarchical':
            from sklearn.cluster import AgglomerativeClustering
            model = AgglomerativeClustering(n_clusters=n_clusters)
            labels = model.fit_predict(X_scaled)
        else:
            return {'success': False, 'error': f'不支持的聚类算法: {algorithm}'}
        
        # 将聚类结果添加到原始数据
        X_with_clusters = pd.DataFrame(X_scaled, columns=valid_features)
        X_with_clusters['cluster'] = labels
        
        # 创建图表
        plt.figure(figsize=(12, 8))
        
        # 如果是二维数据，直接绘制散点图
        if len(valid_features) == 2:
            fig, ax = plt.subplots(figsize=(10, 6))
            scatter = ax.scatter(X_scaled[:, 0], X_scaled[:, 1], 
                      c=labels, cmap='viridis', s=50, alpha=0.8)
            
            # 添加聚类中心（对于KMeans）
            if algorithm == 'kmeans':
                centers = model.cluster_centers_
                ax.scatter(centers[:, 0], centers[:, 1], c='red', 
                         s=100, alpha=0.8, marker='X')
            
            plt.colorbar(scatter, label='聚类标签')
            plt.xlabel(valid_features[0])
            plt.ylabel(valid_features[1])
            plt.title(f'聚类分析结果（算法: {algorithm}, 聚类数: {n_clusters}）')
            plt.grid(True, linestyle='--', alpha=0.7)
            
        # 如果是多维数据，使用PCA降维后绘制
        else:
            from sklearn.decomposition import PCA
            pca = PCA(n_components=2)
            X_pca = pca.fit_transform(X_scaled)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            scatter = ax.scatter(X_pca[:, 0], X_pca[:, 1], 
                      c=labels, cmap='viridis', s=50, alpha=0.8)
            
            # 添加聚类中心（对于KMeans，需要将中心点也进行PCA转换）
            if algorithm == 'kmeans':
                centers = model.cluster_centers_
                centers_pca = pca.transform(centers)
                ax.scatter(centers_pca[:, 0], centers_pca[:, 1], c='red', 
                         s=100, alpha=0.8, marker='X')
            
            plt.colorbar(scatter, label='聚类标签')
            plt.xlabel('主成分 1')
            plt.ylabel('主成分 2')
            plt.title(f'聚类分析结果（算法: {algorithm}, 聚类数: {n_clusters}，PCA降维后）')
            plt.grid(True, linestyle='--', alpha=0.7)
            
            # 添加方差解释图
            explained_variance = pca.explained_variance_ratio_ * 100
            plt.figtext(0.02, 0.02, f'主成分1解释方差: {explained_variance[0]:.2f}%\n'
                        f'主成分2解释方差: {explained_variance[1]:.2f}%',
                        fontsize=10)
        
        # 保存图表
        app_root = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        image_dir = os.path.join(app_root, 'static', 'images')
        os.makedirs(image_dir, exist_ok=True)
            
        filename = f"cluster_{algorithm}_{uuid.uuid4().hex}.png"
        image_path = os.path.join(image_dir, filename)
        
        plt.tight_layout()
        plt.savefig(image_path)
        plt.close('all')
        
        # 获取每个聚类的样本数量
        cluster_counts = pd.Series(labels).value_counts().sort_index().to_dict()
        
        # 垃圾回收
        import gc
        gc.collect()
        
        return {
            'success': True,
            'image_path': image_path,
            'cluster_counts': cluster_counts,
            'algorithm': algorithm,
            'n_clusters': n_clusters,
            'feature_count': len(valid_features)
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        plt.close('all')
        
        return {
            'success': False,
            'error': str(e)
        } 