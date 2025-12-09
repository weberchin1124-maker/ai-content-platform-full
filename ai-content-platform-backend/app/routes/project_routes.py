# app/routes/project_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
# ✨ 引入 AI 服務 (用於週報)
from app.services.ai_service import summarize_project_notes 

project_bp = Blueprint("projects", __name__)

# 輔助函數：延遲導入模型 (避免循環引用)
def get_project_models():
    from app.models import Project, ProjectMember, Content # ✨ 加載 Content 模型
    return Project, ProjectMember, Content

# ==========================================
# 1. 取得我的專案列表 (GET /api/projects)
# ==========================================
@project_bp.route("", methods=["GET"])
@jwt_required()
def get_my_projects():
    try:
        Project, ProjectMember, _ = get_project_models()
        user_id = get_jwt_identity()
        
        # 查詢 ProjectMember 表，找出該使用者參與的所有專案
        memberships = ProjectMember.query.filter_by(user_id=user_id).all()
        
        projects = []
        for m in memberships:
            p = m.project
            if p: 
                projects.append({
                    "project_id": p.project_id,
                    "name": p.name,
                    "description": p.description,
                    "role": m.role,
                    "created_at": p.created_at.isoformat() if hasattr(p, 'created_at') and p.created_at else None
                })
        
        return jsonify(projects), 200
    except Exception as e:
        print(f"Error getting projects: {str(e)}")
        return jsonify({"error": "無法取得專案列表"}), 500


# ==========================================
# 2. 建立新專案 (POST /api/projects)
# ==========================================
@project_bp.route("", methods=["POST"])
@jwt_required()
def create_project():
    try:
        Project, ProjectMember, _ = get_project_models()
        user_id = get_jwt_identity()

        data = request.get_json() or {}
        name = data.get("name")
        description = data.get("description", "")

        if not name:
            return jsonify({"message": "專案名稱必填"}), 400

        # 1. 建立專案本體
        project = Project(
            name=name,
            description=description,
            owner_id=user_id,
        )
        db.session.add(project)
        db.session.flush() # 先 flush 拿到 project_id

        # 2. 建立成員關聯 (把自己設為 owner)
        member = ProjectMember(
            project_id=project.project_id,
            user_id=user_id,
            role="owner",
        )
        db.session.add(member)
        
        db.session.commit()

        return jsonify({
            "message": "Project created",
            "project_id": project.project_id,
            "name": project.name,
            "description": project.description,
            "owner_id": project.owner_id,
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error creating project: {str(e)}")
        return jsonify({"error": "建立專案失敗", "details": str(e)}), 500
    
   
# ==========================================
# 3. 刪除專案 (DELETE /api/projects/<id>)
# ==========================================
@project_bp.route('/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    try:
        user_id = get_jwt_identity()
        Project, ProjectMember, Content = get_project_models() 
        
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({"message": "專案不存在"}), 404
        if str(project.owner_id) != str(user_id):
            return jsonify({"message": "無權限刪除"}), 403
            
        # 1. 刪除所有相關的 Content
        Content.query.filter_by(project_id=project_id).delete()
        
        # 2. 刪除所有相關的 ProjectMember
        ProjectMember.query.filter_by(project_id=project_id).delete()

        # 3. 刪除專案本體
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({"message": "專案已永久刪除"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ==========================================
# 4. ✨ 專案週報 (AI Summary)
# ==========================================
@project_bp.route('/<int:project_id>/summary', methods=['GET'])
@jwt_required()
def get_project_summary(project_id):
    try:
        user_id = get_jwt_identity()
        Project, _, Content = get_project_models()
        
        # 1. 檢查專案是否存在
        project = Project.query.get(project_id)
        if not project:
            return jsonify({"error": "專案不存在"}), 404

        # 2. 抓取該專案最近 10 筆筆記 (依時間倒序)
        contents = Content.query.filter_by(project_id=project_id)\
            .order_by(Content.created_at.desc())\
            .limit(10).all()
            
        if not contents:
            return jsonify({"summary": "目前沒有足夠的筆記可生成報告。"}), 200

        # 3. 整理資料給 AI
        notes_data = []
        for c in contents:
            # 透過 Content 模型的 property 取得最新版 prompt
            if c.prompt:
                notes_data.append({
                    "date": c.created_at.strftime("%Y-%m-%d"),
                    "content": c.prompt 
                })

        if not notes_data:
             return jsonify({"summary": "筆記內容為空，無法生成週報。"}), 200

        # 4. 呼叫 AI 服務
        print(f"📊 正在為專案 {project_id} 生成週報...")
        summary_text = summarize_project_notes(notes_data)
        
        return jsonify({"summary": summary_text}), 200

    except Exception as e:
        import traceback
        print(f"Summary Error: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500