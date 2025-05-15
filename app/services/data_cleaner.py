import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import LabelEncoder
import itertools

def read_file(file_path, file_type):
    """读取数据文件"""
    if file_type == 'csv':
        return pd.read_csv(file_path)
    elif file_type in ['xlsx', 'xls']:
        return pd.read_excel(file_path)
    else:
        raise ValueError(f"不支持的文件类型: {file_type}")

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
        
        # 将 NaN 值替换为 None，这样在 JSON 序列化时会变成 null
        df = df.replace({np.nan: None})
        
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
        original_columns = list(df.columns)
        
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
                
                if method == 'drop':
                    # 删除含有缺失值的行
                    df = df.dropna(subset=[column])
                elif method == 'mean' and pd.api.types.is_numeric_dtype(df[column]):
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
                
            elif op_type == 'drop_duplicates':
                # 删除重复行
                columns = op.get('columns', [])
                keep = op.get('keep', 'first')
                
                if columns:
                    df = df.drop_duplicates(subset=columns, keep=keep)
                else:
                    df = df.drop_duplicates(keep=keep)
                    
            elif op_type == 'handle_outliers':
                # 处理异常值
                if pd.api.types.is_numeric_dtype(df[column]):
                    method = op.get('method', 'drop')
                    threshold = op.get('threshold', 1.5)
                    
                    # 计算IQR和异常值边界
                    Q1 = df[column].quantile(0.25)
                    Q3 = df[column].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - threshold * IQR
                    upper_bound = Q3 + threshold * IQR
                    
                    if method == 'drop':
                        # 删除异常值
                        df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
                    elif method == 'cap':
                        # 截断异常值
                        df[column] = df[column].clip(lower=lower_bound, upper=upper_bound)
                    
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
                    le = LabelEncoder()
                    df[column] = le.fit_transform(df[column])
        
        # 计算行列变化情况
        cleaned_count = len(df)
        removed_count = original_count - cleaned_count
        column_count = len(df.columns)
        added_column_count = len(df.columns) - len(original_columns)
        
        # 创建备份文件（但不作为主要修改文件）
        backup_path = file_path + '.bak'
        if not os.path.exists(backup_path):
            if file_type == 'csv':
                read_file(file_path, file_type).to_csv(backup_path, index=False)
            else:
                read_file(file_path, file_type).to_excel(backup_path, index=False)
        
        # 直接保存到原始文件
        if file_type == 'csv':
            df.to_csv(file_path, index=False)
        else:
            df.to_excel(file_path, index=False)
            
        # 将 NaN 值替换为 None，这样在 JSON 序列化时会变成 null
        df_preview = df.replace({np.nan: None})
        
        # 获取列信息 (与 preview_data 函数返回格式保持一致)
        columns_info = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            # 判断数据类型
            if np.issubdtype(df[col].dtype, np.number):
                data_type = 'numeric'
            elif dtype == 'object':
                data_type = 'categorical'
            else:
                data_type = 'other'
                
            columns_info.append({
                'name': col,
                'type': data_type,
                'missing_count': int(df[col].isna().sum()),
                'unique_count': int(df[col].nunique())
            })
            
        # 返回清洗后的预览和统计信息
        return {
            'success': True,
            'preview': df_preview.head(10).to_dict(orient='records'),
            'original_count': original_count,
            'cleaned_count': cleaned_count,
            'removed_count': removed_count,
            'column_count': column_count,
            'added_column_count': added_column_count,
            'columns': columns_info
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

def detect_duplicates(df):
    """检测重复数据并生成清洗建议"""
    suggestions = []
    
    # 检查整行重复
    duplicate_rows = df.duplicated().sum()
    if duplicate_rows > 0:
        duplicate_ratio = duplicate_rows / len(df)
        priority = 'high' if duplicate_ratio > 0.05 else 'medium'
        
        suggestions.append({
            'type': 'drop_duplicates',
            'columns': [],  # 空列表表示检查所有列
            'keep': 'first',
            'reason': f'发现{duplicate_rows}行完全重复数据 ({duplicate_ratio:.2%})',
            'priority': priority
        })
    
    # 检查特定列组合的重复
    # 针对分类型和ID型特征列查找可能的重复
    categorical_columns = [col for col in df.columns if df[col].dtype == 'object' and df[col].nunique() < len(df) * 0.5]
    
    # 尝试常见的ID列名
    id_columns = [col for col in df.columns if 'id' in col.lower() or 'key' in col.lower() or 'code' in col.lower()]
    
    # 组合这些列查找重复
    columns_to_check = categorical_columns + id_columns
    if len(columns_to_check) > 1 and len(columns_to_check) < 5:  # 只检查少量列的组合，避免计算太复杂
        for i in range(2, min(4, len(columns_to_check) + 1)):
            for columns_combo in itertools.combinations(columns_to_check, i):
                duplicate_count = df.duplicated(subset=list(columns_combo)).sum()
                if duplicate_count > 0:
                    suggestions.append({
                        'type': 'drop_duplicates',
                        'columns': list(columns_combo),
                        'keep': 'first',
                        'reason': f'在列 {", ".join(columns_combo)} 中发现{duplicate_count}条重复记录',
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
        
        # 检测重复数据
        duplicate_suggestions = detect_duplicates(df)
        suggestions.extend(duplicate_suggestions)
        
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