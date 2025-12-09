from ..extensions import db
from ..models import Content, ContentVersion

def create_content_logic(project_id, user_id, data):
    """
    處理建立內容的完整流程：SQL 寫入 -> (未來) NoSQL 寫入 -> 提交
    """
    try:
        # 1. SQL: 建立 Content
        content = Content(
            project_id=project_id,
            creator_user_id=user_id,
            title=data.get("title"),
            primary_type=data.get("primary_type", "text"),
            source_tool=data.get("source_tool"),
        )
        db.session.add(content)
        db.session.flush() # 取得 content_id

        # 2. (未來) NoSQL: 在這裡呼叫 MongoDB/VectorDB 寫入 Prompt/Response
        # nosql_id = insert_to_mongodb(data.get("prompt"), ...)
        nosql_id = None # 暫時範例

        # 3. SQL: 建立 Version
        version = ContentVersion(
            content_id=content.content_id,
            created_by=user_id,
            version_number=1,
            prompt=data.get("prompt"),
            file_url=data.get("file_url"),
            # response_ref=nosql_id  <-- 之後把 NoSQL ID 存進來
        )
        db.session.add(version)
        db.session.flush()

        # 4. SQL: 更新 Latest Version 指標
        content.latest_version_id = version.version_id
        
        db.session.commit()
        return content, version
        
    except Exception as e:
        db.session.rollback() # 發生任何錯誤（含 NoSQL 連線失敗），全部取消
        raise e
