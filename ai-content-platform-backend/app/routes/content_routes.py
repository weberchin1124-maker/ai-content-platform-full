# app/routes/content_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
# 引入兩個模型：Content 和 ContentVersion
from app.models import Project, Content, ContentVersion, Tag 

content_bp = Blueprint('content', __name__)

# ==========================================
# 1. 新增內容 (Create Content + Version 1)
# ==========================================
@content_bp.route('/project/<int:project_id>', methods=['POST'])
@jwt_required()
def create_content_for_project(project_id):
    try:
        user_id = get_jwt_identity()
        
        # 1. 檢查專案是否存在
        project = Project.query.get(project_id)
        if not project: return jsonify({"error": "Project not found"}), 404

        data = request.get_json()
        
        # 2. 建立 Content 外殼
        new_content = Content(
            project_id=project_id,
            creator_user_id=user_id,
            title=data.get('title', '無標題'),
            primary_type=data.get('primary_type', 'text'),
            source_tool=data.get('source_tool', 'Manual')
        )
        db.session.add(new_content)
        db.session.flush() # 先取得 content_id

        # 3. 建立第一版 Version
        new_version = ContentVersion(
            content_id=new_content.content_id,
            created_by=user_id,
            version_number=1, # 第一版
            prompt=data.get('prompt', ''),
            response=data.get('response', '')
        )
        
        # 4. 處理標籤
        tags_input = data.get('tags', [])
        for tag_name in tags_input:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            new_content.tags.append(tag)

        db.session.add(new_version)
        db.session.flush() # 取得 version_id

        # 5. 回填 latest_version_id (指向最新版)
        new_content.latest_version_id = new_version.version_id
        
        db.session.commit()
        
        return jsonify({
            "message": "Content created", 
            "id": new_content.content_id,
            "title": new_content.title
        }), 201

    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"ERROR: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500


# ==========================================
# 2. 編輯內容 (Create New Version) -> 🚀 核心改動
# ==========================================
@content_bp.route('/<int:content_id>', methods=['PUT'])
@jwt_required()
def update_content(content_id):
    try:
        user_id = get_jwt_identity()
        content = Content.query.get(content_id)
        
        if not content: return jsonify({"message": "Not found"}), 404
        
        # 檢查權限
        if str(content.creator_user_id) != str(user_id):
             return jsonify({"message": "無權限修改"}), 403

        data = request.get_json()
        
        # 1. 找出目前最新的版本號
        current_latest = None
        if content.latest_version:
            current_latest = content.latest_version
        
        # 版本號 + 1
        next_ver_num = (current_latest.version_number + 1) if current_latest else 1
        
        # 2. 建立新版本 (INSERT，不是 UPDATE)
        # 如果前端只傳了 prompt，我們要把舊的 response 複製過來，避免資料遺失
        new_prompt = data.get('prompt', current_latest.prompt if current_latest else "")
        new_response = data.get('response', current_latest.response if current_latest else "")

        new_version = ContentVersion(
            content_id=content_id,
            created_by=user_id,
            version_number=next_ver_num, 
            prompt=new_prompt,
            response=new_response
        )
        
        db.session.add(new_version)
        db.session.flush()
        
        # 3. 更新 Content 的指針指向新版本
        content.latest_version_id = new_version.version_id
        
        db.session.commit()
        
        return jsonify({
            "message": "Version updated", 
            "new_version": next_ver_num
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ==========================================
# 3. 取得內容 (GET) - 自動抓取 Latest Version
# ==========================================
@content_bp.route('/project/<int:project_id>', methods=['GET'])
@jwt_required()
def get_contents_by_project(project_id):
    try:
        # 抓取該專案所有內容，新的在上面
        contents = Content.query.filter_by(project_id=project_id).order_by(Content.created_at.desc()).all()
        
        results = []
        for c in contents:
            # 透過 relationship 取得最新版本資料
            latest = c.latest_version
            
            # 如果資料庫異常沒有 latest，就給空值
            prompt_text = latest.prompt if latest else ""
            response_text = latest.response if latest else ""
            
            results.append({
                "id": c.content_id,
                "project_id": c.project_id,
                "title": c.title,
                "prompt": prompt_text,
                "response": response_text,
                "tags": [t.name for t in c.tags],
                "date": c.created_at.isoformat() if c.created_at else None,
                "version": latest.version_number if latest else 0 # 告訴前端這是第幾版
            })
        return jsonify(results), 200
    except Exception as e:
        print(f"Get Error: {e}")
        return jsonify({"error": str(e)}), 500

# ==========================================
# 4. 刪除內容 (Cascade Delete)
# ==========================================
@content_bp.route('/<int:content_id>', methods=['DELETE'])
@jwt_required()
def delete_content(content_id):
    try:
        content = Content.query.get(content_id)
        if content:
            # SQLAlchemy 的 cascade 會自動把 versions 刪掉
            db.session.delete(content)
            db.session.commit()
            return jsonify({"message": "Deleted"}), 200
        return jsonify({"message": "Not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500