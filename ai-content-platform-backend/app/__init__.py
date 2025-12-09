# app/__init__.py
from flask import Flask, jsonify
from .config import Config
# ✅ 引入我們寫好的初始化函式 (取代原本個別引入 db, bcrypt...)
from .extensions import init_extensions 

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # =================================================
    # 🚀 關鍵修改：呼叫 init_extensions 來啟動所有套件
    # 這會同時啟動 SQL、JWT、CORS 和 MongoDB
    # =================================================
    init_extensions(app)

    # ==================================
    # 🔗 註冊藍圖 (Blueprints) - 路由總機
    # ==================================
    
    # 1. 會員系統 (Login/Register) -> /api/auth
    from .routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # 2. 專案系統 (Projects) -> /api/projects
    from .routes.project_routes import project_bp
    app.register_blueprint(project_bp, url_prefix='/api/projects')

    # 3. 內容系統 (Contents) -> /api/contents
    from .routes.content_routes import content_bp
    app.register_blueprint(content_bp, url_prefix='/api/contents')

    # 4. 搜尋系統 (Search) -> /api/search
    from .routes.search_routes import search_bp
    app.register_blueprint(search_bp, url_prefix='/api/search')

    # 全域 404 錯誤處理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "The requested URL was not found on the server.", "success": False}), 404

    # 全域 500 錯誤處理
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal Server Error", "success": False}), 500

    # ==========================================
    # 🖨️ 印出目前已註冊的路由 (方便除錯)
    # ==========================================
    print("\n🔗 目前已註冊的路由 (Routes):")
    for rule in app.url_map.iter_rules():
        # 過濾掉 static 路由，只顯示 API
        if "static" not in str(rule):
            print(f" - {rule} ({','.join(rule.methods)})")
    print("-" * 30 + "\n")

    return app