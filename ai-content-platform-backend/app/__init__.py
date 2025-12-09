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

    # 初始化 Mongo (如果 MONGO_URI 有設定)
    init_mongo(app)

    # 註冊藍圖（延後導入以避免循環依賴）
    from .routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    from .routes.project_routes import project_bp
    app.register_blueprint(project_bp, url_prefix='/api/projects')

    from .routes.content_routes import content_bp
    app.register_blueprint(content_bp, url_prefix='/api/contents')

    from .routes.search_routes import search_bp
    app.register_blueprint(search_bp, url_prefix='/api/search')

    from .routes.tag_routes import tag_bp
    app.register_blueprint(tag_bp, url_prefix='/api/tags')

    from .routes.version_routes import version_bp
    app.register_blueprint(version_bp, url_prefix='/api/version')

    # 健康檢查路由（方便測試）
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({"status": "ok"}), 200

    # 全域 404 錯誤處理 (讓前端收到 JSON 而不是 HTML)
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "The requested URL was not found on the server.", "success": False}), 404

    # 全域 500 錯誤處理
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal Server Error", "success": False}), 500

    return app