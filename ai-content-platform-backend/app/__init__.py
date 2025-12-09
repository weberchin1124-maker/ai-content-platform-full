
# app/__init__.py
from flask import Flask, jsonify
from flask_cors import CORS
from .extensions import db, bcrypt, jwt, init_mongo
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 初始化套件
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    CORS(app) # 允許跨域
    
    # 初始化 MongoDB (如果有設定 MONGO_URI)
    init_mongo(app)

    # ==================================
    # 🔗 註冊藍圖 (Blueprints) - 路由總機
    # ==================================
    
    # 1. 會員系統 (Login/Register) -> /api/auth
    from .routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # 2. 專案系統 (Projects) -> /api/projects
    # 如果你還沒建立 project_routes，這行可能會報錯，可以先註解掉
    from .routes.project_routes import project_bp
    app.register_blueprint(project_bp, url_prefix='/api/projects')

    # 3. 內容系統 (Contents) -> /api/contents (注意有 s)
    from .routes.content_routes import content_bp
    app.register_blueprint(content_bp, url_prefix='/api/contents')

    # 4. 搜尋系統 (Search) -> /api/search
    from .routes.search_routes import search_bp
    app.register_blueprint(search_bp, url_prefix='/api/search')
    
    # 5. 標籤系統 (Tags) -> /api/tags
    from .routes.tag_routes import tag_bp
    app.register_blueprint(tag_bp, url_prefix='/api/tags')
    
    # 6. 版本系統 (Versions) -> /api/versions
    from .routes.version_routes import version_bp
    app.register_blueprint(version_bp, url_prefix='/api/versions')

    # 健康檢查端點
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            "status": "healthy",
            "message": "API is running"
        }), 200

    # 全域 404 錯誤處理 (讓前端收到 JSON 而不是 HTML)
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "The requested URL was not found on the server.", "success": False}), 404

    # 全域 500 錯誤處理
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal Server Error", "success": False}), 500

    return app