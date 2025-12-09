# app/routes/content_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
# ✨ 引入 mongo_db
from app.extensions import db, mongo_db 
from app.models import Project, Content, ContentVersion, Tag 

content_bp = Blueprint('content', __name__)

# ==========================================
# 🔧 輔助函式：寫入 MongoDB
# ==========================================
def save_to_nosql(data_dict):
    """
    將非結構化內容寫入 MongoDB 並回傳 ID (字串格式)
    如果 MongoDB 沒連線，會跳過並回傳 None (不會讓程式崩潰)
    """
    if mongo_db is None:
        print("⚠️ MongoDB not connected, skipping NoSQL write.")
        return None
    try:
        # 加上寫入時間
        data_dict["created_at"] = datetime.utcnow()
        
        # 寫入 'contents' 集合 (Collection)
        result = mongo_db.contents.insert_one(data_dict)
        
        # 回傳 ObjectId 字串
        return str(result.inserted_id)
    except Exception as e:
        print(f"❌ NoSQL Write Error: {e}")
        return None

# ==========================================
# 1. 新增內容 (SQL + NoSQL 雙寫)
# ==========================================
@content_bp.route('/project/<int:project_id>', methods=['POST'])
@jwt_required()
def create_content_for_project(project_id):
    try:
        user_id = get_jwt_identity()
        project = Project.query.get(project_id)
        if not project: return jsonify({"error": "Project not found"}), 404

        data = request.get_json()
        
        # 1. SQL: 建立 Content 外殼
        new_content = Content(
            project_id=project_id,
            creator_user_id=user_id,
            title=data.get('title', '無標題'),
            primary_type=data.get('primary_type', 'text'),
            source_tool=data.get('source_tool', 'Manual')
        )
        db.session.add(new_content)
        db.session.flush() # 取得 content_id

        # 2. ✨ NoSQL: 先寫入 MongoDB
        # 這邊存入完整的非結構化資料
        nosql_data = {
            "project_id": project_id,
            "user_id": user_id,
            "version_number": 1,
            "prompt": data.get('prompt', ''),
            "response": data.get('response', ''),
            "tags": data.get('tags', []),
            "metadata": {"source": "Hybrid_System", "type": "initial_creation"}
        }
        nosql_id = save_to_nosql(nosql_data)

        # 3. SQL: 建立第一版 Version (並關聯 NoSQL ID)
        new_version = ContentVersion(
            content_id=new_content.content_id,
            created_by=user_id,
            version_number=1, 
            prompt=data.get('prompt', ''),
            response=data.get('response', ''),
            # ✨ 把 MongoDB 的 ID 存進來 (達成關聯)
            response_ref=nosql_id 
        )
        
        # 4. SQL: 處理標籤
        tags_input = data.get('tags', [])
        for tag_name in tags_input:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            new_content.tags.append(tag)

        db.session.add(new_version)
        db.session.flush() # 取得 version_id

        # 5. SQL: 回填 latest_version_id
        new_content.latest_version_id = new_version.version_id
        
        db.session.commit()
        
        return jsonify({
            "message": "Content created (Hybrid)", 
            "id": new_content.content_id,
            "title": new_content.title,
            "nosql_id": nosql_id # 回傳給前端看 (證明有存)
        }), 201

    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"ERROR: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500


# ==========================================
# 2. 編輯內容 (SQL + NoSQL 雙寫)
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
        
        # 計算版本號
        current_latest = content.latest_version
        next_ver_num = (current_latest.version_number + 1) if current_latest else 1
        
        # 準備資料
        new_prompt = data.get('prompt', current_latest.prompt if current_latest else "")
        new_response = data.get('response', current_latest.response if current_latest else "")

        # 1. ✨ NoSQL: 寫入新版本文件
        nosql_data = {
            "content_id": content_id,
            "project_id": content.project_id,
            "user_id": user_id,
            "version_number": next_ver_num,
            "prompt": new_prompt,
            "response": new_response,
            "metadata": {"source": "Hybrid_System", "type": "version_update"}
        }
        nosql_id = save_to_nosql(nosql_data)

        # 2. SQL: 建立新版本記錄
        new_version = ContentVersion(
            content_id=content_id,
            created_by=user_id,
            version_number=next_ver_num, 
            prompt=new_prompt,
            response=new_response,
            # ✨ 關聯 MongoDB ID
            response_ref=nosql_id
        )
        
        db.session.add(new_version)
        db.session.flush()
        
        # 3. SQL: 更新指標
        content.latest_version_id = new_version.version_id
        
        db.session.commit()
        
        return jsonify({
            "message": "Version updated (Hybrid)", 
            "new_version": next_ver_num,
            "nosql_id": nosql_id
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ==========================================
# 3. 取得內容 (讀取 SQL metadata)
# ==========================================
@content_bp.route('/project/<int:project_id>', methods=['GET'])
@jwt_required()
def get_contents_by_project(project_id):
    try:
        contents = Content.query.filter_by(project_id=project_id).order_by(Content.created_at.desc()).all()
        
        results = []
        for c in contents:
            latest = c.latest_version
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
                "version": latest.version_number if latest else 0,
                # ✨ 回傳 NoSQL ID 證明關聯存在
                "nosql_ref": latest.response_ref if latest else None 
            })
        return jsonify(results), 200
    except Exception as e:
        print(f"Get Error: {e}")
        return jsonify({"error": str(e)}), 500

# ==========================================
# 4. 刪除內容
# ==========================================
@content_bp.route('/<int:content_id>', methods=['DELETE'])
@jwt_required()
def delete_content(content_id):
    try:
        content = Content.query.get(content_id)
        if content:
            # SQL Cascade 會自動刪除 ContentVersion
            # (NoSQL 資料通常保留作為稽核，或需另外寫排程刪除，MVP 先不刪)
            db.session.delete(content)
            db.session.commit()
            return jsonify({"message": "Deleted"}), 200
        return jsonify({"message": "Not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500