# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS # 記得加這個，不然前端會連不上
from pymongo import MongoClient

# 初始化 Flask 套件物件
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
cors = CORS()

# ✅ 全域變數：讓其他檔案 (如 routes) 可以 import 使用
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
    
    # 開放跨域請求 (讓 React 可以呼叫 API)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # 2. 初始化 MongoDB 連線
    global mongo_client, mongo_db
    
    # 從設定讀取 URI，如果沒設定就預設連本機
    uri = app.config.get("MONGO_URI", "mongodb://localhost:27017/")
    
    try:
        # 設定 timeout 為 2 秒，避免連不上時卡住程式
        mongo_client = MongoClient(uri, serverSelectionTimeoutMS=2000)
        
        # 測試連線 (Ping)
        mongo_client.admin.command('ping')
        
        # 指定資料庫名稱 (建議固定一個名字，方便管理)
        mongo_db = mongo_client["ai_content_platform"]
        
        print("✅ MongoDB Atlas/Local Connected Successfully!")
        
    except Exception as e:
        print(f"⚠️ MongoDB Connection Failed: {e}")
        print("   -> 系統將降級為「純 SQL 模式」運作")
        mongo_client = None
        mongo_db = None