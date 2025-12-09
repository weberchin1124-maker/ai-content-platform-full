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
        # 盡量把 JWT 身分轉回 int，避免 type mismatch
        user_id = get_jwt_identity()
        try:
            user_id = int(user_id)
        except Exception:
            pass

        # 1. 檢查專案是否存在且使用者是否有權限 (簡化檢查)
        project = Project.query.get(project_id)
        if not project:
            return {"msg": "Project not found"}, 404
        
        # 2. 資料驗證與接收
        try:
            validated_data = content_creation_schema.load(request.json)
        except Exception as err:
            # 返回 400 Bad Request 和詳細錯誤訊息
            return {"msg": "Input validation failed", "errors": getattr(err, "messages", str(err))}, 400

        # 3. 建立新的 Content 實例（把 creator_user_id 改為 user_id）
        new_content = Content(
            project_id=project_id,
            user_id=user_id,
            title=validated_data['title'],
            primary_type=validated_data['primary_type'],
            source_tool=validated_data.get('source_tool'),
            original_prompt=validated_data.get('prompt', ''),
            generated_content=validated_data.get('response', ''),
        )
        db.session.add(new_content)
        
        # 確保 Content 被建立，以便獲得 content_id
        db.session.flush() 

        # 4. 處理標籤（schema 裡的欄位名是 tags）
        tag_names = validated_data.get('tags', [])
        
        if tag_names:
            existing_tags = Tag.query.filter(Tag.name.in_(tag_names)).all()
            existing_tag_names = {tag.name for tag in existing_tags}
            
            new_tag_names = [name for name in tag_names if name not in existing_tag_names]
            
            new_tags = [Tag(name=name, created_by=user_id) for name in new_tag_names]
            db.session.add_all(new_tags)
            
            all_tags = existing_tags + new_tags

            # 建立 ContentTag 關聯記錄
            for tag in all_tags:
                association = ContentTag(
                    content_id=new_content.content_id, 
                    tag_id=tag.tag_id
                )
                db.session.add(association)

        # 5. 提交所有變更
        db.session.commit()
        
        # 6. 回傳結果
        return {"msg": "Content and tags created successfully", "content_id": new_content.content_id}, 201