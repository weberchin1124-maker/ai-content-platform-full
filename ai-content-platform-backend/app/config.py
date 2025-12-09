import os
from dotenv import load_dotenv
from datetime import timedelta # ✅ 新增：為了設定 Token 時效

# 載入 .env 檔案中的環境變數
load_dotenv()

# Get the base directory
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # 格式: postgresql://username:password@host:port/database
    # 如果環境變數中有 DATABASE_URL 就用它，否則用 sqlite 作為 fallback
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # Use absolute path for SQLite
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, '..', 'instance', 'dev.db')}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 安全設定
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    
    # ✅ [關鍵修正] 設定 Token 一天後才過期 (解決一直被踢出的問題)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    
    # ✅ [關鍵修正] 必須加上這行，Flask 才知道要讀取 MONGO_URI
    MONGO_URI = os.getenv("MONGO_URI")

    # 專案指定的 Schema (第九組 g9)
    PG_SCHEMA = os.getenv("PG_SCHEMA", "g9")