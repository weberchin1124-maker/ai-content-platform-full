# app/routes/search_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from app.extensions import db
# ✅ 關鍵修改：引入 ContentVersion 模型
from app.models import Content, Project, Tag, ContentVersion

search_bp = Blueprint("search", __name__)

@search_bp.route("", methods=["GET"])
@jwt_required()
def search_contents():
    """
    全能搜尋 API (SQL 版本控制修復版)
    用法: GET /api/search?q=關鍵字
    """
    try:
        user_id = get_jwt_identity()
        query_text = request.args.get("q", "").strip()

        # 1. 如果沒有輸入關鍵字，回傳空陣列
        if not query_text:
            return jsonify({"count": 0, "results": []}), 200

        print(f"DEBUG: 使用者 {user_id} 正在搜尋: {query_text}")

        search_pattern = f"%{query_text}%"

        # 2. 執行 SQL 查詢
        # 🚀 關鍵修正：加入 ContentVersion 的 Join
        # 邏輯變更：
        #   - Join Project (確認權限)
        #   - Join ContentVersion (透過 latest_version_id 找到最新版內容)
        #   - Left Join Tag (搜尋標籤)
        results = db.session.query(Content)\
            .join(Project, Content.project_id == Project.project_id)\
            .join(ContentVersion, Content.latest_version_id == ContentVersion.version_id)\
            .outerjoin(Content.tags)\
            .filter(Project.owner_id == user_id)\
            .filter(
                or_(
                    Content.title.ilike(search_pattern),             # 搜標題
                    ContentVersion.prompt.ilike(search_pattern),     # ✅ 改搜 Version 的 prompt
                    ContentVersion.response.ilike(search_pattern),   # ✅ 改搜 Version 的 response
                    Tag.name.ilike(search_pattern)                   # 搜標籤
                )
            )\
            .order_by(Content.created_at.desc())\
            .distinct()\
            .limit(50)\
            .all()

        # 3. 整理回傳資料
        response_data = []
        for c in results:
            # 取得最新版本物件
            latest = c.latest_version
            
            response_data.append({
                "id": c.id,
                "project_id": c.project_id,
                "project_name": c.project.name,
                
                # ✅ 從最新版本讀取內容 (防呆：如果沒有版本就給空字串)
                "prompt": latest.prompt if latest else "",
                "response": latest.response if latest else "",
                "version": latest.version_number if latest else 0, # 告訴前端這是第幾版
                
                "tags": [t.name for t in c.tags],
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "source_tool": c.source_tool
            })

        return jsonify({
            "count": len(response_data),
            "keyword": query_text,
            "results": response_data
        }), 200

    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"❌ Search Error: {error_msg}")
        return jsonify({"error": "搜尋發生錯誤", "details": str(e)}), 500