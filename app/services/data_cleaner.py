import pandas as pd
import numpy as np
import os

def read_file(file_path, file_type):
    """读取数据文件"""
    if file_type == 'csv':
        return pd.read_csv(file_path)
    elif file_type in ['xlsx', 'xls']:
        return pd.read_excel(file_path)
    else:
        raise ValueError(f"不支持的文件类型: {file_type}")

def preview_data(file_path=None, n_rows=5):
    """
    模拟预览数据文件（简化版）
    """
    # 返回模拟数据
    sample_data = pd.DataFrame({
        'col1': [1, 2, 3, 4, 5],
        'col2': ['a', 'b', 'c', 'd', 'e']
    })
    
    info = {
        'columns': ['col1', 'col2'],
        'shape': (5, 2),
        'dtypes': {'col1': 'int64', 'col2': 'object'}
    }
    
    return sample_data, info

def clean_data(file_path=None, na_strategy='drop', numeric_cols=None, categorical_cols=None):
    """
    模拟清洗数据（简化版）
    """
    # 返回模拟清洗后的数据
    return pd.DataFrame({
        'col1': [1, 2, 3, 4, 5],
        'col2': ['a', 'b', 'c', 'd', 'e']
    })

def preview_data(file_path, file_type, rows=10):
    """预览数据，返回前几行、总行数和列信息"""
    try:
        df = read_file(file_path, file_type)
        
        # 获取列信息
        columns = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            # 判断数据类型
            if np.issubdtype(df[col].dtype, np.number):
                data_type = 'numeric'
            elif dtype == 'object':
                data_type = 'categorical'
            else:
                data_type = 'other'
                
            columns.append({
                'name': col,
                'type': data_type,
                'missing_count': int(df[col].isna().sum()),
                'unique_count': int(df[col].nunique())
            })
        
        # 转换为列表形式，便于JSON序列化
        preview_data = df.head(rows).to_dict(orient='records')
        
        return preview_data, len(df), columns
    except Exception as e:
        return [], 0, []

def clean_data(file_path, file_type, operations):
    """根据指定的操作清洗数据"""
    try:
        df = read_file(file_path, file_type)
        original_count = len(df)
        
        for op in operations:
            op_type = op.get('type')
            column = op.get('column')
            
            if op_type == 'drop_column':
                # 删除列
                df = df.drop(columns=[column])
                
            elif op_type == 'fill_na':
                # 填充缺失值
                method = op.get('method', 'mean')
                value = op.get('value')
                
                if method == 'mean' and pd.api.types.is_numeric_dtype(df[column]):
                    df[column] = df[column].fillna(df[column].mean())
                elif method == 'median' and pd.api.types.is_numeric_dtype(df[column]):
                    df[column] = df[column].fillna(df[column].median())
                elif method == 'mode':
                    df[column] = df[column].fillna(df[column].mode()[0])
                elif method == 'value' and value is not None:
                    df[column] = df[column].fillna(value)
                    
            elif op_type == 'drop_na':
                # 删除包含缺失值的行
                df = df.dropna(subset=[column])
                
            elif op_type == 'remove_outliers':
                # 移除异常值 (使用IQR方法)
                if pd.api.types.is_numeric_dtype(df[column]):
                    Q1 = df[column].quantile(0.25)
                    Q3 = df[column].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
                    
            elif op_type == 'categorical_encoding':
                # 分类变量编码
                method = op.get('method', 'one_hot')
                
                if method == 'one_hot':
                    # 独热编码
                    dummies = pd.get_dummies(df[column], prefix=column)
                    df = pd.concat([df.drop(column, axis=1), dummies], axis=1)
                    
                elif method == 'label':
                    # 标签编码
                    from sklearn.preprocessing import LabelEncoder
                    le = LabelEncoder()
                    df[column] = le.fit_transform(df[column])
        
        # 保存清洗后的数据
        cleaned_path = file_path.replace('.', '_cleaned.')
        
        if file_type == 'csv':
            df.to_csv(cleaned_path, index=False)
        else:
            df.to_excel(cleaned_path, index=False)
            
        # 返回清洗后的预览和统计信息
        return {
            'success': True,
            'preview': df.head(10).to_dict(orient='records'),
            'original_count': original_count,
            'cleaned_count': len(df),
            'removed_count': original_count - len(df)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def detect_missing_values(df):
    """检测缺失值并生成清洗建议"""
    suggestions = []
    
    for col in df.columns:
        missing_count = df[col].isna().sum()
        if missing_count > 0:
            missing_ratio = missing_count / len(df)
            
            if missing_ratio > 0.5:
                # 超过50%缺失，建议删除此列
                suggestions.append({
                    'type': 'drop_column',
                    'column': col,
                    'reason': f'此列超过50%的值缺失 ({missing_count}/{len(df)})',
                    'priority': 'high'
                })
            elif pd.api.types.is_numeric_dtype(df[col]):
                # 数值列，建议用均值或中位数填充
                suggestions.append({
                    'type': 'fill_na',
                    'column': col,
                    'method': 'mean',
                    'reason': f'数值列有{missing_count}个缺失值，建议用均值填充',
                    'priority': 'medium'
                })
            else:
                # 分类列，建议用众数填充
                suggestions.append({
                    'type': 'fill_na',
                    'column': col,
                    'method': 'mode',
                    'reason': f'分类列有{missing_count}个缺失值，建议用众数填充',
                    'priority': 'medium'
                })
    
    return suggestions

def detect_outliers(df):
    """检测异常值并生成清洗建议"""
    suggestions = []
    
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            # 使用IQR方法检测异常值
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
            outlier_count = len(outliers)
            
            if outlier_count > 0 and outlier_count < len(df) * 0.1:  # 少于10%是异常值
                suggestions.append({
                    'type': 'remove_outliers',
                    'column': col,
                    'reason': f'发现{outlier_count}个异常值',
                    'priority': 'medium'
                })
    
    return suggestions

def auto_suggest_cleaning(file_path, file_type):
    """自动分析数据并提供清洗建议"""
    try:
        df = read_file(file_path, file_type)
        
        suggestions = []
        
        # 检测缺失值
        missing_suggestions = detect_missing_values(df)
        suggestions.extend(missing_suggestions)
        
        # 检测异常值
        outlier_suggestions = detect_outliers(df)
        suggestions.extend(outlier_suggestions)
        
        # 检测分类变量，提供编码建议
        for col in df.columns:
            if df[col].dtype == 'object' and df[col].nunique() < len(df) * 0.2:  # 唯一值较少的列
                suggestions.append({
                    'type': 'categorical_encoding',
                    'column': col,
                    'method': 'one_hot' if df[col].nunique() < 10 else 'label',
                    'reason': f'分类变量，建议进行编码',
                    'priority': 'low'
                })
        
        return {
            'success': True,
            'suggestions': suggestions
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        } 