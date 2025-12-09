# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from pymongo import MongoClient

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

# ✅ [關鍵修改] 宣告全域變數，讓 content_routes 可以 import 它們
mongo_client = None
mongo_db = None

def init_mongo(app):
    global mongo_client, mongo_db
    
    # 從設定讀取 URI
    uri = app.config.get("MONGO_URI")
    
    if uri:
        try:
            # 連線 MongoDB
            mongo_client = MongoClient(uri)
            # 測試連線 (Ping)
            mongo_client.admin.command('ping')
            print("✅ MongoDB Atlas Connected!")
            
            # 指定資料庫名稱 (你可以自己取，例如 g9_project)
            mongo_db = mongo_client["g9_project"]
        except Exception as e:
            print(f"❌ MongoDB Connection Failed: {e}")
    else:
        print("⚠️ No MONGO_URI found in config.")