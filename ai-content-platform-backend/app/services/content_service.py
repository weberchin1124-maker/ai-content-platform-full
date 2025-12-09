from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.extensions import db, mongo_db 
from app.models import Project, Content, ContentVersion, Tag 
# ✨ 引入所有 AI 功能
from app.services.ai_service import generate_ai_content, generate_tags_from_text, refine_text_content

content_bp = Blueprint('content', __name__)

def save_to_nosql(data_dict):
    if mongo_db is None: return None
    try:
        data_dict["created_at"] = datetime.utcnow()
        result = mongo_db.contents.insert_one(data_dict)
        return str(result.inserted_id)
    except Exception as e:
        print(f"❌ NoSQL Error: {e}")
        return None

# ==========================================
# 1. 新增內容 (整合 自動對話 + 自動標籤)
# ==========================================
@content_bp.route('/project/<int:project_id>', methods=['POST'])
@jwt_required()
def create_content_for_project(project_id):
    try:
        user_id = get_jwt_identity()
        project = Project.query.get(project_id)
        if not project: return jsonify({"error": "Project not found"}), 404

        data = request.get_json()
        user_prompt = data.get('prompt', '')
        ai_response = data.get('response', '')
        tags_input = data.get('tags', [])
        source_tool = data.get('source_tool', 'Manual')

        # 🤖 AI 功能 1：自動對話 (使用者沒填 response)
        if not ai_response and user_prompt:
            ai_response = generate_ai_content(user_prompt)
            source_tool = "Gemini AI"

        # 🤖 AI 功能 2：自動標籤 (使用者沒填 tags)
        if not tags_input and user_prompt:
            print("🏷️ 正在自動生成標籤...")
            tags_input = generate_tags_from_text(user_prompt)

        # 1. SQL: 建立 Content
        new_content = Content(
            project_id=project_id,
            creator_user_id=user_id,
            title=data.get('title', user_prompt[:20]),
            primary_type="text",
            source_tool=source_tool
        )
        db.session.add(new_content)
        db.session.flush()

        # 2. NoSQL
        nosql_id = save_to_nosql({
            "project_id": project_id,
            "user_id": user_id,
            "version_number": 1,
            "prompt": user_prompt,
            "response": ai_response,
            "tags": tags_input,
            "metadata": {"type": "initial_creation"}
        })

        # 3. SQL Version
        new_version = ContentVersion(
            content_id=new_content.content_id,
            created_by=user_id,
            version_number=1, 
            prompt=user_prompt,
            response=ai_response,
            response_ref=nosql_id 
        )
        
        # 4. 處理標籤
        for tag_name in tags_input:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            new_content.tags.append(tag)

        db.session.add(new_version)
        db.session.commit()
        
        return jsonify({
            "message": "Content created", 
            "id": new_content.content_id,
            "response": ai_response,
            "tags": tags_input, # 回傳 AI 產生的標籤
            "nosql_id": nosql_id 
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ==========================================
# 2. ✨ AI 一鍵美化 (Refine)
# ==========================================
@content_bp.route('/<int:content_id>/refine', methods=['POST'])
@jwt_required()
def refine_content(content_id):
    try:
        user_id = get_jwt_identity()
        content = Content.query.get(content_id)
        if not content: return jsonify({"message": "Not found"}), 404

        # 1. 取得最新內容
        current_text = content.prompt 
        print("✨ 正在美化筆記...")
        
        # 2. 呼叫 AI
        refined_text = refine_text_content(current_text)
        
        # 3. 存為新版本 (Version Control)
        next_ver = content.latest_version.version_number + 1
        
        nosql_id = save_to_nosql({
            "content_id": content_id,
            "version_number": next_ver,
            "prompt": refined_text,
            "response": content.response,
            "metadata": {"type": "ai_refine"}
        })

        new_version = ContentVersion(
            content_id=content_id,
            created_by=user_id,
            version_number=next_ver,
            prompt=refined_text, # 存入美化後的內容
            response=content.response,
            response_ref=nosql_id
        )
        
        db.session.add(new_version)
        db.session.flush()
        content.latest_version_id = new_version.version_id
        db.session.commit()

        return jsonify({
            "message": "Content Refined",
            "new_prompt": refined_text,
            "version": next_ver
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ... (請務必保留原本的 update_content, get_contents_by_project, delete_content，放在這裡下面) ...
# (為了篇幅，這裡省略這三個函式，請確認你的檔案裡還有它們！)
# ==========================================
# 3. 編輯內容 (一般更新)
# ==========================================
@content_bp.route('/<int:content_id>', methods=['PUT'])
@jwt_required()
def update_content(content_id):
    try:
        user_id = get_jwt_identity()
        content = Content.query.get(content_id)
        if not content: return jsonify({"message": "Not found"}), 404
        
        if str(content.creator_user_id) != str(user_id):
             return jsonify({"message": "無權限修改"}), 403

        data = request.get_json()
        current_latest = content.latest_version
        next_ver_num = (current_latest.version_number + 1) if current_latest else 1
        
        new_prompt = data.get('prompt', current_latest.prompt if current_latest else "")
        new_response = data.get('response', current_latest.response if current_latest else "")

        # NoSQL
        nosql_id = save_to_nosql({
            "content_id": content_id,
            "version_number": next_ver_num,
            "prompt": new_prompt,
            "response": new_response,
            "metadata": {"type": "version_update"}
        })

        # SQL
        new_version = ContentVersion(
            content_id=content_id,
            created_by=user_id,
            version_number=next_ver_num, 
            prompt=new_prompt,
            response=new_response,
            response_ref=nosql_id
        )
        
        db.session.add(new_version)
        db.session.flush()
        content.latest_version_id = new_version.version_id
        db.session.commit()
        
        return jsonify({
            "message": "Version updated", 
            "new_version": next_ver_num,
            "nosql_id": nosql_id
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@content_bp.route('/project/<int:project_id>', methods=['GET'])
@jwt_required()
def get_contents_by_project(project_id):
    try:
        contents = Content.query.filter_by(project_id=project_id).order_by(Content.created_at.desc()).all()
        results = []
        for c in contents:
            latest = c.latest_version
            results.append({
                "id": c.content_id,
                "project_id": c.project_id,
                "title": c.title,
                "prompt": latest.prompt if latest else "",
                "response": latest.response if latest else "",
                "tags": [t.name for t in c.tags],
                "date": c.created_at.isoformat() if c.created_at else None,
                "version": latest.version_number if latest else 0,
                "nosql_ref": latest.response_ref if latest else None 
            })
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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