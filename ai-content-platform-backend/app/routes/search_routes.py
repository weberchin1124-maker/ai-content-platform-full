# app/routes/search_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from app.extensions import db
# 引入我們剛剛定義好的 SQL 模型
from app.models import Content, Project, Tag

search_bp = Blueprint("search", __name__)

@search_bp.route("", methods=["GET"])  # 注意：這裡設為空字串或 "/" 皆可，對應 /api/search
@jwt_required()
def search_contents():
    """
    全能搜尋 API (SQL 版)
    用法: GET /api/search?q=關鍵字
    功能: 同時搜尋 標題、筆記內容、AI回覆、標籤
    """
    try:
        user_id = get_jwt_identity()
        query_text = request.args.get("q", "").strip()

        # 1. 如果沒有輸入關鍵字，回傳空陣列 (或你可以選擇回傳所有內容)
        if not query_text:
            return jsonify({"count": 0, "results": []}), 200

        print(f"DEBUG: 使用者 {user_id} 正在搜尋: {query_text}")

        # 2. 建構搜尋字串 (前後加 % 代表模糊搜尋)
        search_pattern = f"%{query_text}%"

        # 3. 執行 SQL 查詢
        # 邏輯：
        #   - 從 Content 表開始查
        #   - Join Project 表 (為了確認這筆內容是該使用者的)
        #   - Left Join Tags 表 (為了讓標籤也能被搜到)
        #   - Filter: 專案擁有者必須是自己
        #   - Filter: (標題 符合 OR 內容 符合 OR 回覆 符合 OR 標籤名稱 符合)
        results = db.session.query(Content)\
            .join(Project, Content.project_id == Project.project_id)\
            .outerjoin(Content.tags)\
            .filter(Project.owner_id == user_id)\
            .filter(
                or_(
                    Content.title.ilike(search_pattern),             # 搜標題
                    Content.original_prompt.ilike(search_pattern),   # 搜筆記內容
                    Content.generated_content.ilike(search_pattern), # 搜 AI 回覆
                    Tag.name.ilike(search_pattern)                   # 搜標籤
                )
            )\
            .order_by(Content.created_at.desc())\
            .distinct()\
            .limit(50)\
            .all()

        # 4. 整理回傳資料 (配合前端 Dashboard.jsx 的格式)
        response_data = []
        for c in results:
            response_data.append({
                "id": c.id,          # 前端需要 id
                "mongo_id": c.id,    # 相容舊前端欄位 (可選)
                "project_id": c.project_id,
                "project_name": c.project.name, # 順便告訴前端這是哪個專案的
                "prompt": c.prompt,       # 使用 property 存取
                "response": c.response,   # 使用 property 存取
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