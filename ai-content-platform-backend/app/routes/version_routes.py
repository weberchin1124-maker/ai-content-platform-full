#版本管理 API：新增版本、列出版本
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import (
    ProjectMember,
    Content,
    ContentVersion,
)

version_bp = Blueprint("version", __name__)


def _user_in_project(user_id, project_id):
    return (
        ProjectMember.query
        .filter_by(user_id=user_id, project_id=project_id)
        .first()
        is not None
    )


@version_bp.route("/content/<int:content_id>", methods=["GET"])
@jwt_required()
def list_versions(content_id):
    """列出某個 content 的所有版本"""
    user_id = get_jwt_identity()

    content = Content.query.get(content_id)
    if not content:
        return jsonify({"message": "content 不存在"}), 404

    if not _user_in_project(user_id, content.project_id):
        return jsonify({"message": "你沒有這個專案的權限"}), 403

    versions = (
        ContentVersion.query
        .filter_by(content_id=content_id)
        .order_by(ContentVersion.version_number.desc())
        .all()
    )

    result = []
    for v in versions:
        result.append({
            "version_id": v.version_id,
            "version_number": v.version_number,
            "created_by": v.created_by,
            "created_at": v.created_at.isoformat() if v.created_at else None,
            "prompt": v.prompt,
            "file_url": v.file_url,
            "response_ref": str(v.response_ref) if v.response_ref else None,
        })

    return jsonify(result), 200


@version_bp.route("/content/<int:content_id>", methods=["POST"])
@jwt_required()
def create_new_version(content_id):
    """
    幫某個 content 新增一個版本
    body 範例：
    {
      "prompt": "更新後的 prompt",
      "file_url": null
    }
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    content = Content.query.get(content_id)
    if not content:
        return jsonify({"message": "content 不存在"}), 404

    if not _user_in_project(user_id, content.project_id):
        return jsonify({"message": "你沒有這個專案的權限"}), 403

    prompt = data.get("prompt")
    file_url = data.get("file_url")

    # 找現在最大版號
    last_version = (
        ContentVersion.query
        .filter_by(content_id=content_id)
        .order_by(ContentVersion.version_number.desc())
        .first()
    )
    next_version_number = (last_version.version_number + 1) if last_version else 1

    new_version = ContentVersion(
        content_id=content_id,
        created_by=user_id,
        version_number=next_version_number,
        prompt=prompt,
        file_url=file_url,
    )
    db.session.add(new_version)
    db.session.flush()

    # 手動更新 latest_version_id（就算 DB 有 trigger，這樣做也沒差）
    content.latest_version_id = new_version.version_id

    db.session.commit()

    return jsonify({
        "content_id": content_id,
        "version_id": new_version.version_id,
        "version_number": new_version.version_number,
    }), 201
