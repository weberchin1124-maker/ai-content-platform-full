# fix_db.py
from app import create_app
from app.extensions import db
from app.models import Tag, ContentTag

# 如果您的 app 工廠函數需要參數，請依據 run.py 調整
app = create_app()

with app.app_context():
    print("正在檢查資料庫連線...")
    try:
        print("正在強制建立所有缺少的資料表 (包含 Tag)...")
        db.create_all()
        print("\n✅ 資料表修復成功！Tag 與 ContentTag 表已建立。")
    except Exception as e:
        print(f"\n❌ 建立失敗: {e}")