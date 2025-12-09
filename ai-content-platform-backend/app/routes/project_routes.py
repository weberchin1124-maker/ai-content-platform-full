# app/routes/project_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db

project_bp = Blueprint("projects", __name__)

# 輔助函數：延遲導入模型 (這是為了避免循環導入的好方法，保留！)
def get_project_models():
    from app.models import Project, ProjectMember 
    return Project, ProjectMember

# ==========================================
# 1. 取得我的專案列表 (GET /api/projects)
# ==========================================
@project_bp.route("", methods=["GET"])
@jwt_required()
def get_my_projects():
    try:
        # 內部取得模型
        Project, ProjectMember = get_project_models() 
        user_id = get_jwt_identity()
        
        # 邏輯：查詢 ProjectMember 表，找出該使用者參與的所有專案
        memberships = ProjectMember.query.filter_by(user_id=user_id).all()
        
        # 透過關聯取出 Project 物件
        projects = []
        for m in memberships:
            p = m.project
            if p: 
                projects.append({
                    "project_id": p.project_id,
                    "name": p.name,
                    "description": p.description,
                    "role": m.role,
                    # 確保時間轉成字串，避免 JSON 報錯
                    "created_at": p.created_at.isoformat() if hasattr(p, 'created_at') and p.created_at else None
                })
        
        # (選擇性) 這裡可以依照時間排序，讓新專案排在前面
        # projects.sort(key=lambda x: x['created_at'] or '', reverse=True)
        
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
        # 內部取得模型
        Project, ProjectMember = get_project_models()
        user_id = get_jwt_identity()

        data = request.get_json() or {}
        name = data.get("name")
        description = data.get("description", "") # 給預設值，防止 None

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
        
        # 3. 提交到資料庫
        db.session.commit()

        # ✅ 關鍵修改：回傳前端看得懂的 message
        return jsonify({
            "message": "Project created", # 前端在等這句話！
            "project_id": project.project_id,
            "name": project.name,
            "description": project.description,
            "owner_id": project.owner_id,
        }), 201

    except Exception as e:
        db.session.rollback() # 發生錯誤要回滾，避免資料庫卡住
        print(f"Error creating project: {str(e)}") # 印出錯誤到終端機
        return jsonify({"error": "建立專案失敗", "details": str(e)}), 500
    
   
# ==========================================
# 🗑️ 刪除專案 (DELETE /api/projects/<id>)
# ==========================================
@project_bp.route('/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    try:
        user_id = get_jwt_identity()
        from app.models import Project, Content, ProjectMember # 確保引入 Content 和 ProjectMember
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({"message": "專案不存在"}), 404
        if str(project.owner_id) != str(user_id):
            return jsonify({"message": "無權限刪除"}), 403
            
        # 🚨 關鍵修復：手動刪除所有相關內容和成員
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