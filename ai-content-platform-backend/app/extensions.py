# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS 
from pymongo import MongoClient
import certifi # ✅ 關鍵 1：引入 certifi 套件

# 初始化 Flask 套件物件
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
cors = CORS()

# 全域變數
mongo_client = None
mongo_db = None

def init_extensions(app):
    """
    初始化所有擴充套件 (SQL, JWT, Bcrypt, CORS, MongoDB)
    """
    # 1. 初始化標準 Flask 套件
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    
    # 開放跨域請求
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # 2. 初始化 MongoDB 連線
    global mongo_client, mongo_db
    
    # 從設定讀取 URI
    uri = app.config.get("MONGO_URI", "mongodb://localhost:27017/")
    
    try:
        # ✅ 關鍵 2：加入 tlsCAFile=certifi.where() 解決 SSL 錯誤
        # 同時將 timeout 延長至 5000ms (5秒) 避免網路波動導致連線失敗
        mongo_client = MongoClient(
            uri, 
            serverSelectionTimeoutMS=5000, 
            tlsCAFile=certifi.where() 
        )
        
        # 測試連線 (Ping)
        mongo_client.admin.command('ping')
        
        # 指定資料庫名稱
        mongo_db = mongo_client["ai_content_platform"]
        
        print("✅ MongoDB Atlas Connected Successfully (with SSL)!")
        
    except Exception as e:
        print(f"⚠️ MongoDB Connection Failed: {e}")
        print("   -> 系統將降級為「純 SQL 模式」運作")
        mongo_client = None
        mongo_db = None