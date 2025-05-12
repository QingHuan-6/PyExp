import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import uuid
from app.services.data_cleaner import read_file
from flask import current_app

def create_visualization(file_path, file_type, chart_type, config):
    """根据配置创建可视化图表"""
    try:
        df = read_file(file_path, file_type)
        
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
            
            if hue:
                sns.lineplot(data=df, x=x, y=y, hue=hue)
            else:
                sns.lineplot(data=df, x=x, y=y)
            
            plt.title(config.get('title', f'Line Chart - {y} over {x}'))
            
        elif chart_type == 'scatter':
            x = config.get('x')
            y = config.get('y')
            hue = config.get('hue')
            
            if not x or not y:
                return {'success': False, 'error': '缺少必要的参数: x和y'}
            
            if hue:
                sns.scatterplot(data=df, x=x, y=y, hue=hue)
            else:
                sns.scatterplot(data=df, x=x, y=y)
            
            plt.title(config.get('title', f'Scatter Plot - {y} vs {x}'))
            
        elif chart_type == 'histogram':
            x = config.get('x')
            bins = config.get('bins', 10)
            
            if not x:
                return {'success': False, 'error': '缺少必要的参数: x'}
            
            sns.histplot(data=df, x=x, bins=bins)
            plt.title(config.get('title', f'Histogram of {x}'))
            
        elif chart_type == 'heatmap':
            columns = config.get('columns', [])
            
            if not columns or len(columns) < 2:
                return {'success': False, 'error': '需要至少两列进行热图分析'}
            
            # 计算相关性
            corr = df[columns].corr()
            sns.heatmap(corr, annot=True, cmap='coolwarm')
            plt.title(config.get('title', 'Correlation Heatmap'))
            
        elif chart_type == 'box':
            x = config.get('x')
            y = config.get('y')
            
            if not y:
                return {'success': False, 'error': '缺少必要的参数: y'}
            
            if x:
                sns.boxplot(data=df, x=x, y=y)
            else:
                sns.boxplot(data=df, y=y)
            
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
        plt.close()
        
        return {
            'success': True,
            'image_path': image_path
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        } 