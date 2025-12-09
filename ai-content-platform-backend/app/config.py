# app/config.py
import os
from dotenv import load_dotenv
from datetime import timedelta 

# 載入 .env 檔案
load_dotenv()

class Config:
    # 1. 資料庫連線設定 (Supabase PostgreSQL)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:aA11423040%40@db.jfryzpggvqstuzrbdpkp.supabase.co:5432/postgres"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 2. 安全設定 & Token 時效
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-key")
    
    # 設定 Token 為 1 天後才過期
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    
    # 3. NoSQL 設定 (MongoDB)
    # 如果 .env 沒設定，預設連本機 mongodb://localhost:27017/ai_content_platform
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/ai_content_platform")

    # 4. ✅ AI 設定 (新增這行，讀取 .env 中的 Key)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # 5. 其他設定
    PG_SCHEMA = os.getenv("PG_SCHEMA", "g9")