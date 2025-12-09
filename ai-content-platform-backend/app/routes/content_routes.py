# app/routes/content_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Project, Content, Tag 

content_bp = Blueprint('content', __name__)

# ==========================================
# 1. 新增內容 (POST)
# ==========================================
@content_bp.route('/project/<int:project_id>', methods=['POST'])
@jwt_required()
def create_content_for_project(project_id):
    try:
        # 1. 檢查專案
        project = Project.query.get(project_id)
        if not project:
            return jsonify({"error": "Project not found"}), 404

        data = request.get_json()
        
        # 2. 建立內容
        new_content = Content(
            title=data.get('title', 'No Title'),
            primary_type=data.get('primary_type', 'text'),
            
            # ✅ 這裡很重要：對應 models.py 的 prompt 屬性
            original_prompt=data.get('prompt', ''), 
            
            # ✅ 這裡很重要：對應 models.py 的 response 屬性
            generated_content=data.get('response', ''), 
            
            source_tool=data.get('source_tool', 'Manual'),
            project_id=project_id,
            
            # 🚨 修正重點：改回 user_id (配合你的 models.py)
            user_id=int(get_jwt_identity())
        )
        
        # 3. 處理標籤
        tags_input = data.get('tags', [])
        for tag_name in tags_input:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            new_content.tags.append(tag)

        db.session.add(new_content)
        db.session.commit()
        return jsonify({"message": "Content created", "id": new_content.id}), 201
        
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"Create Error Trace: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

# ==========================================
# 2. 取得內容 (GET)
# ==========================================
@content_bp.route('/project/<int:project_id>', methods=['GET'])
@jwt_required()
def get_contents_by_project(project_id):
    try:
        contents = Content.query.filter_by(project_id=project_id).order_by(Content.id.desc()).all()
        
        results = []
        for c in contents:
            results.append({
                "id": c.id,
                # ✅ 透過 property 存取
                "prompt": c.prompt,     
                "response": c.response, 
                "tags": [t.name for t in c.tags],
                "date": c.created_at.isoformat() if c.created_at else None
            })
        return jsonify(results), 200
    except Exception as e:
        print(f"Get Error: {e}")
        return jsonify({"error": str(e)}), 500

# ==========================================
# 3. 刪除與更新 (DELETE / PUT)
# ==========================================
@content_bp.route('/<int:content_id>', methods=['DELETE'])
@jwt_required()
def delete_content(content_id):
    try:
        content = Content.query.get(content_id)
        if content:
            db.session.delete(content)
            db.session.commit()
            return jsonify({"message": "Deleted"}), 200
        return jsonify({"message": "Not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@content_bp.route('/<int:content_id>', methods=['PUT'])
@jwt_required()
def update_content(content_id):
    try:
        content = Content.query.get(content_id)
        if content:
            data = request.get_json()
            # 使用 setter 更新
            content.prompt = data.get('prompt', content.prompt)
            db.session.commit()
            return jsonify({"message": "Updated"}), 200
        return jsonify({"message": "Not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500