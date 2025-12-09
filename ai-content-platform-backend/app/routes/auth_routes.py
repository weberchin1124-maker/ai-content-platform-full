# app/routes/auth_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..extensions import db, bcrypt
# 移除所有模型導入！

auth_bp = Blueprint("auth", __name__)


# 輔助函數：延遲導入模型
# 註：將導入 User 的邏輯，使用絕對導入，幫助 Python 繞過循環
def get_user_model():
    """在需要時才導入 User 模型"""
    from app.models import User # ✅ 使用絕對導入
    return User


@auth_bp.route("/register", methods=["POST"])
def register():
    User = get_user_model() # 內部取得模型
    
    data = request.get_json() or {}
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")

    if not email or not username or not password:
        return jsonify({"message": "email, username, password 欄位必填"}), 400

    # 檢查 email 是否重複
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "此 email 已被註冊"}), 400

    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    user = User(email=email, username=username, password_hash=pw_hash)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "註冊成功"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    User = get_user_model() # 內部取得模型
    
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "email 和 password 必填"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"message": "帳號或密碼錯誤"}), 401

    access_token = create_access_token(identity=str(user.user_id))

    return jsonify({
        "access_token": access_token,
        "user": {
            "id": user.user_id,
            "email": user.email,
            "username": user.username,
        },
    }), 200


@auth_bp.route("/update", methods=["PUT"])
@jwt_required()
def update_user():
    User = get_user_model() # 內部取得模型

    user_id = get_jwt_identity()
    user = User.query.get(user_id) 
    
    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    
    if 'username' in data and data['username']:
        user.username = data['username']
        
    if 'new_password' in data and data['new_password']:
        hashed_password = bcrypt.generate_password_hash(data['new_password']).decode('utf-8')
        user.password_hash = hashed_password
        
    try:
        db.session.commit()
        return jsonify({
            "message": "更新成功",
            "user": {
                "id": user.user_id,
                "email": user.email,
                "username": user.username
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Update failed: {str(e)}"}), 500