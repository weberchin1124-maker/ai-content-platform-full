# app/routes/content_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.extensions import db, mongo_db 
from app.models import Project, Content, ContentVersion, Tag 
# ✨ 引入 AI 服務
from app.services.ai_service import generate_ai_content, generate_tags_from_text, refine_text_content

content_bp = Blueprint('content', __name__)

# ==========================================
# 🔧 輔助函式：寫入 MongoDB
# ==========================================
def save_to_nosql(data_dict):
    if mongo_db is None:
        print("⚠️ MongoDB not connected, skipping NoSQL write.")
        return None
    try:
        data_dict["created_at"] = datetime.utcnow()
        result = mongo_db.contents.insert_one(data_dict)
        return str(result.inserted_id)
    except Exception as e:
        print(f"❌ NoSQL Write Error: {e}")
        return None

# ==========================================
# 1. 新增內容 (自動標籤 + AI 生成)
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
        source_tool = data.get('source_tool', 'Manual')
        tags_input = data.get('tags', [])
        
        # ✨ 1. 讀取前端傳來的模型名稱 (如果沒傳就預設 flash)
        selected_model = data.get('model', 'gemini-1.5-flash')

        # 🤖 AI 場景 0: 自動生成內容
        if not ai_response and user_prompt:
            print(f"🤖 正在呼叫 AI 生成內容... 使用模型: {selected_model}")
            # ✨ 2. 關鍵修正：將 model_name 傳入函式
            ai_response = generate_ai_content(user_prompt, model_name=selected_model)
            
            # 更新來源標記
            model_display = selected_model.replace("gemini-", "").title()
            source_tool = f"Gemini {model_display}"

        # 🤖 AI 場景 1: 自動生成標籤 (Auto-Tagging)
        if not tags_input and user_prompt:
            print("🏷️ 正在呼叫 AI 自動生成標籤...")
            # ✨ 3. 關鍵修正：標籤生成也使用選定的模型 (或你可以固定用 flash)
            tags_input = generate_tags_from_text(user_prompt, model_name=selected_model)
            print(f"✅ AI 建議標籤: {tags_input}")

        # 1. SQL: 建立 Content
        new_content = Content(
            project_id=project_id,
            creator_user_id=user_id,
            title=data.get('title', user_prompt[:20]), 
            primary_type=data.get('primary_type', 'text'),
            source_tool=source_tool
        )
        db.session.add(new_content)
        db.session.flush()

        # 2. NoSQL: 寫入 MongoDB
        nosql_data = {
            "project_id": project_id,
            "user_id": user_id,
            "version_number": 1,
            "prompt": user_prompt,
            "response": ai_response,
            "tags": tags_input,
            "metadata": {"source": source_tool, "type": "initial_creation", "model": selected_model}
        }
        nosql_id = save_to_nosql(nosql_data)

        # 3. SQL: 建立 Version
        new_version = ContentVersion(
            content_id=new_content.content_id,
            created_by=user_id,
            version_number=1, 
            prompt=user_prompt,
            response=ai_response,
            response_ref=nosql_id 
        )
        
        # 4. SQL: 處理標籤
        for tag_name in tags_input:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            new_content.tags.append(tag)

        db.session.add(new_version)
        db.session.flush()
        new_content.latest_version_id = new_version.version_id
        db.session.commit()
        
        return jsonify({
            "message": "Content created", 
            "id": new_content.content_id,
            "title": new_content.title,
            "response": ai_response,
            "tags": tags_input,
            "nosql_id": nosql_id 
        }), 201

    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"ERROR: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500


# ==========================================
# 2. 編輯內容 (一般更新)
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

# ==========================================
# 3. 🤖 AI 場景 2: 一鍵美化 (Refine)
# ==========================================
@content_bp.route('/<int:content_id>/refine', methods=['POST'])
@jwt_required()
def refine_content(content_id):
    try:
        user_id = get_jwt_identity()
        content = Content.query.get(content_id)
        if not content: return jsonify({"message": "Not found"}), 404

        data = request.get_json() or {}
        # ✨ 1. 讀取前端傳來的模型
        selected_model = data.get('model', 'gemini-1.5-flash')

        current_text = content.prompt 
        print(f"✨ 正在美化筆記... 使用模型: {selected_model}")
        
        # ✨ 2. 關鍵修正：將 model_name 傳入函式
        refined_text = refine_text_content(current_text, model_name=selected_model)
        
        # 3. 直接存成「新版本」
        next_ver_num = content.latest_version.version_number + 1
        
        # 寫入 NoSQL
        nosql_id = save_to_nosql({
            "content_id": content_id,
            "version_number": next_ver_num,
            "prompt": refined_text,
            "response": content.response,
            "metadata": {"type": "ai_refine", "model": selected_model}
        })

        # 寫入 SQL Version
        new_version = ContentVersion(
            content_id=content_id,
            created_by=user_id,
            version_number=next_ver_num,
            prompt=refined_text, 
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
            "version": next_ver_num
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ==========================================
# 4. 取得內容 & 刪除 (保持原樣)
# ==========================================
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