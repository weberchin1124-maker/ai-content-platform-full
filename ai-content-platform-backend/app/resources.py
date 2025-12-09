# app/resources.py

from flask import request
from flask.views import MethodView
from app.extensions import db # 確保導入您的 db 實例
from app.models import (
    Content, 
    ContentTag, 
    Tag, 
    Project # 需要檢查 Project 是否存在
)
from app.schemas import ContentCreationSchema, ContentResponseSchema
from flask_jwt_extended import jwt_required, get_jwt_identity # 假設您使用 JWT 進行認證

# 實例化 Schema
content_creation_schema = ContentCreationSchema()
content_response_schema = ContentResponseSchema()


class ContentListResource(MethodView):
    """處理 /api/contents/project/<project_id> 的 API 邏輯"""
    
    # 確保只有登入的使用者才能存取
    @jwt_required()
    def post(self, project_id):
        user_id = get_jwt_identity()

        # 1. 檢查專案是否存在且使用者是否有權限 (簡化檢查)
        project = Project.query.get(project_id)
        if not project:
            return {"msg": "Project not found"}, 404
        
        # 註：這裡應該加入 ProjectMember 檢查 user_id 是否在該專案中

        # 2. 資料驗證與接收
        try:
            validated_data = content_creation_schema.load(request.json)
        except Exception as err:
            # 返回 400 Bad Request 和詳細錯誤訊息
            return {"msg": "Input validation failed", "errors": err.messages}, 400

        # 3. 建立新的 Content 實例
        new_content = Content(
            project_id=project_id,
            creator_user_id=user_id,
            title=validated_data['title'],
            primary_type=validated_data['primary_type'],
            source_tool=validated_data.get('source_tool'),
            # 註：這裡還需要處理 ContentVersion 的建立和 latest_version_id 的設定
        )
        db.session.add(new_content)
        
        # 確保 Content 被建立，以便獲得 content_id
        db.session.flush() 

        # 4. 處理標籤
        tag_names = validated_data.get('user_defined_tags', [])
        
        if tag_names:
            # 查詢資料庫中已存在的標籤
            # 使用 .name.in_() 進行批量查詢
            existing_tags = Tag.query.filter(Tag.name.in_(tag_names)).all()
            existing_tag_names = {tag.name for tag in existing_tags}
            
            # 建立不存在的新標籤
            new_tag_names = [name for name in tag_names if name not in existing_tag_names]
            
            new_tags = [Tag(name=name, created_by=user_id) for name in new_tag_names]
            db.session.add_all(new_tags)
            
            all_tags = existing_tags + new_tags

            # 建立 ContentTag 關聯記錄
            for tag in all_tags:
                # 由於 ContentTag 已經調整為聯合主鍵，可以直接建立實例
                association = ContentTag(
                    content_id=new_content.content_id, 
                    tag_id=tag.tag_id
                )
                db.session.add(association)

        # 5. 提交所有變更
        db.session.commit()
        
        # 6. 回傳結果
        # return content_response_schema.dump(new_content), 201
        return {"msg": "Content and tags created successfully", "content_id": new_content.content_id}, 201

# 註冊 API（需在 app/__init__.py 或 routes.py 中完成）
# 範例：app.add_url_rule(
#     "/api/contents/project/<int:project_id>",
#     view_func=ContentListResource.as_view("content_list_api"),
#     methods=["POST"],
# )