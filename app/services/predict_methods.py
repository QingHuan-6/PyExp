import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import xgboost as xgb
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

def load_data(file_path: str) -> pd.DataFrame:
    """加载CSV数据文件
    
    Args:
        file_path: CSV文件路径
        
    Returns:
        加载的数据DataFrame
    """
    # 检查文件存在性
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    # 尝试加载数据
    try:
        df = pd.read_csv(file_path)
        print(f"成功加载数据，共{len(df)}行，{len(df.columns)}列")
        return df
    except Exception as e:
        raise ValueError(f"加载数据出错: {str(e)}")

def preprocess_data(df: pd.DataFrame, training: bool = True, preprocessor_objects: dict = None) -> tuple:
    """执行所有预处理步骤
    
    Args:
        df: 输入数据
        training: 是否为训练模式
        preprocessor_objects: 预处理对象字典(用于测试模式)
        
    Returns:
        (处理后的数据, 预处理对象字典)
    """
    # 创建预处理对象字典
    if training:
        preprocessor_objects = {}
    elif preprocessor_objects is None:
        raise ValueError("测试模式需要提供预处理对象")
    
    # 创建数据副本，避免修改原始数据
    data = df.copy()
    
    # 1. 移除ID列(如果存在)
    id_column = None
    if 'Id' in data.columns:
        id_column = data['Id'].copy()
        data = data.drop('Id', axis=1)
    
    # 2. 分离特征和目标变量(如果在训练模式且存在目标变量)
    target = None
    if training and 'SalePrice' in data.columns:
        target = data['SalePrice'].copy()
        data = data.drop('SalePrice', axis=1)
        
        # 目标变量对数转换(处理偏态)
        preprocessor_objects['log_transform_target'] = True
        target = np.log1p(target)
    
    # 3. 区分数值和分类特征
    numeric_features = []
    categorical_features = []
    
    for col in data.columns:
        # 检查列的类型
        if data[col].dtype == 'object' or data[col].nunique() < 10:
            categorical_features.append(col)
        else:
            numeric_features.append(col)
    
    preprocessor_objects['numeric_features'] = numeric_features
    preprocessor_objects['categorical_features'] = categorical_features
    
    print(f"数值特征: {len(numeric_features)}个, 分类特征: {len(categorical_features)}个")
    
    # 4. 处理缺失值和特征工程
    if training:
        # 4.1 数值特征处理
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        
        # 4.2 分类特征处理
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore', sparse=False))
        ])
        
        # 4.3 组合转换器
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)
            ]
        )
        
        # 4.4 训练预处理器
        features_transformed = preprocessor.fit_transform(data)
        preprocessor_objects['preprocessor'] = preprocessor
        
        # 4.5 保存转换后的特征名称
        cat_feature_names = []
        if categorical_features:
            cat_encoder = preprocessor.named_transformers_['cat'].named_steps['onehot']
            cat_cols = []
            for i, col in enumerate(categorical_features):
                transformed_cols = [f"{col}_{val}" for val in cat_encoder.categories_[i]]
                cat_cols.extend(transformed_cols)
            cat_feature_names = cat_cols
        
        feature_names = numeric_features + cat_feature_names
        preprocessor_objects['feature_names'] = feature_names
        
    else:
        # 使用已有的预处理器转换数据
        preprocessor = preprocessor_objects['preprocessor']
        features_transformed = preprocessor.transform(data)
    
    # 创建转换后的特征DataFrame
    columns = preprocessor_objects['feature_names']
    features_df = pd.DataFrame(features_transformed, columns=columns)
    
    return (features_df, target, id_column, preprocessor_objects)

def train_model(train_features: pd.DataFrame, train_labels: pd.Series, 
                model_path: str, preprocessor_path: str, 
                preprocessor_objects: dict):
    """训练XGBoost回归模型并保存
    
    Args:
        train_features: 训练特征
        train_labels: 训练标签
        model_path: 模型保存路径
        preprocessor_path: 预处理器保存路径
        preprocessor_objects: 预处理对象字典
    """
    # 划分训练集和验证集
    X_train, X_val, y_train, y_val = train_test_split(
        train_features, train_labels, test_size=0.2, random_state=42
    )
    
    # 创建并训练XGBoost模型
    model = xgb.XGBRegressor(
        objective='reg:squarederror',
        n_estimators=1000,
        learning_rate=0.05,
        max_depth=5,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )
    
    # 训练模型 - 简化版本，不使用早停
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=True
    )
    
    # 在验证集上评估模型
    val_preds = model.predict(X_val)
    rmse = np.sqrt(mean_squared_error(y_val, val_preds))
    r2 = r2_score(y_val, val_preds)
    
    print(f"验证集RMSE: {rmse:.6f}")
    print(f"验证集R²: {r2:.6f}")
    
    # 确保目录存在
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    os.makedirs(os.path.dirname(preprocessor_path), exist_ok=True)
    
    # 保存模型和预处理器
    joblib.dump(model, model_path)
    joblib.dump(preprocessor_objects, preprocessor_path)
    
    print(f"模型已保存到: {model_path}")
    print(f"预处理器已保存到: {preprocessor_path}")
    
    return model

def predict(test_features: pd.DataFrame, model_path: str, preprocessor_path: str) -> np.ndarray:
    """使用训练好的模型进行预测
    
    Args:
        test_features: 测试特征数据
        model_path: 模型路径
        preprocessor_path: 预处理器路径
        
    Returns:
        预测结果数组
    """
    # 加载模型和预处理器
    model = joblib.load(model_path)
    preprocessor_objects = joblib.load(preprocessor_path)
    
    # 预处理测试数据
    features_df, _, id_column, _ = preprocess_data(
        test_features, 
        training=False, 
        preprocessor_objects=preprocessor_objects
    )
    
    # 进行预测
    predictions = model.predict(features_df)
    
    # 如果目标进行了对数转换，则需要逆转换
    if preprocessor_objects.get('log_transform_target', False):
        predictions = np.expm1(predictions)
    
    return predictions, id_column

def full_training_pipeline(train_file_path: str, model_save_path: str, preprocessor_save_path: str):
    """完整的训练流程
    
    Args:
        train_file_path: 训练数据文件路径
        model_save_path: 模型保存路径
        preprocessor_save_path: 预处理器保存路径
    """
    # 加载数据
    df = load_data(train_file_path)
    
    # 预处理数据
    features_df, target, _, preprocessor_objects = preprocess_data(df, training=True)
    
    # 训练模型
    model = train_model(
        features_df, 
        target, 
        model_save_path, 
        preprocessor_save_path, 
        preprocessor_objects
    )
    
    return model, preprocessor_objects

def evaluate_model(model, X_test, y_test):
    """评估模型性能
    
    Args:
        model: 训练好的模型
        X_test: 测试特征
        y_test: 测试标签
        
    Returns:
        包含评估指标的字典
    """
    # 进行预测
    y_pred = model.predict(X_test)
    
    # 计算评估指标
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    
    return {
        'mse': float(mse),
        'rmse': float(rmse),
        'r2': float(r2)
    } 