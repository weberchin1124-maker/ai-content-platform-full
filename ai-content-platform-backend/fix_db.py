from app import create_app
from app.extensions import db
# 確保導入了所有模型，這樣 create_all 才會生效
from app.models import Tag, ContentTag, Content, ContentVersion, Project, ProjectMember, User

app = create_app()

with app.app_context():
    print("正在檢查資料庫連線...")
    try:
        print("正在強制建立所有缺少的資料表...")
        db.create_all()
        print("\n✅ 資料表修復成功！Tag 與 ContentTag 表已建立。")
    except Exception as e:
        print(f"\n❌ 建立失敗: {e}")
