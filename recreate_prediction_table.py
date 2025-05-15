from app.init import app, db, Prediction, recreate_prediction_table

if __name__ == '__main__':
    print("开始重建Prediction表...")
    recreate_prediction_table()
    print("操作完成！") 