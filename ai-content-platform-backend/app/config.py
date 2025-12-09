import os
from dotenv import load_dotenv
from datetime import timedelta 

# 載入 .env 檔案，這會將 .env 中的變數讀取到 os.environ 中
load_dotenv()

class Config:
    # 1. 安全金鑰設定
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-key")
    
    # 2. SQL 設定 (Flask-SQLAlchemy 需要這個鍵)
    DATABASE_URL = os.getenv("DATABASE_URL")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False # 避免產生警告
    
    # JWT 設定
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    
    # 3. NoSQL 設定 (MongoDB)
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/ai_content_platform")

    # 4. AI 設定
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # 5. 其他設定
    PG_SCHEMA = os.getenv("PG_SCHEMA", "g9")