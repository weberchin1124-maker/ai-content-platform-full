# app/routes/auth_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..extensions import db, bcrypt

auth_bp = Blueprint("auth", __name__)

def get_user_model():
    from app.models import User
    return User


@auth_bp.route("/register", methods=["POST"])
def register():
    User = get_user_model()
    
    data = request.get_json() or {}
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")

    if not email or not username or not password:
        return jsonify({"message": "email, username, password 欄位必填"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "此 email 已被註冊"}), 400

    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    user = User(email=email, username=username, password_hash=pw_hash)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "註冊成功"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    User = get_user_model()
    
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "email 和 password 必填"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"message": "帳號或密碼錯誤"}), 401

    # 傳 int identity（較方便在後續當作 int 使用）
    access_token = create_access_token(identity=user.user_id)

    return jsonify({
        "access_token": access_token,
        "user": {
            "id": user.user_id,
            "email": user.email,
            "username": user.username,
        },
    }), 200