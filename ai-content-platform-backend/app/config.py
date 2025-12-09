import os
from dotenv import load_dotenv
from datetime import timedelta # ✅ 新增：為了設定 Token 時效

# 載入 .env 檔案中的環境變數
load_dotenv()

class Config:
    # 格式: postgresql://username:password@host:port/database
    # 這裡將你的 Supabase 連線字串設為預設值 (密碼中的 @ 已改為 %40)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:aA11423040%40@db.jfryzpggvqstuzrbdpkp.supabase.co:5432/postgres"
    )
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