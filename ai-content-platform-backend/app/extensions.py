from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS 
from pymongo import MongoClient
import certifi # 引入 certifi 套件

# 初始化 Flask 套件物件
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
cors = CORS()

# 全域變數：讓其他檔案 (如 routes) 可以 import 使用
mongo_client = None
mongo_db = None


def init_extensions(app):
    """初始化所有 Flask 擴充套件"""
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    
    # 🚨 關鍵修正：開放跨域請求 (允許 Authorization 標頭)
    cors.init_app(app, resources={r"/api/*": {
        "origins": "*",  # 允許所有來源
        # 必須明確允許 Authorization 和 Content-Type 標頭
        "allow_headers": ["Authorization", "Content-Type"] 
    }})

    # 2. 初始化 MongoDB 連線
    global mongo_client, mongo_db
    
    # 從設定讀取 URI
    uri = app.config.get("MONGO_URI", "mongodb://localhost:27017/")
    
    try:
        # 連線至 MongoDB Atlas (使用 SSL 憑證，並延長 timeout)
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