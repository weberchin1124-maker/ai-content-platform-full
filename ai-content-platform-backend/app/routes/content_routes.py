#標籤 API：建立標籤、對 content 加標籤、依標籤查內容
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import (
    Tag,
    ContentTag,
    Content,
    ProjectMember
)

tag_bp = Blueprint("tag", __name__)


def _user_in_project(user_id, project_id):
    try:
        user_id = int(user_id)
    except Exception:
        pass
    return (
        ProjectMember.query
        .filter_by(user_id=user_id, project_id=project_id)
        .first()
        is not None
    )


@tag_bp.route("", methods=["GET"])
@jwt_required()
def list_tags():
    q = request.args.get("q")

    query = Tag.query
    if q:
        query = query.filter(Tag.name.ilike(f"%{q}%"))

    tags = query.order_by(Tag.name.asc()).all()
    result = [
        {"tag_id": t.tag_id, "name": t.name}
        for t in tags
    ]
    return jsonify(result), 200


@tag_bp.route("", methods=["POST"])
@jwt_required()
def create_tag():
    user_id = get_jwt_identity()
    try:
        user_id = int(user_id)
    except Exception:
        pass
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()

    if not name:
        return jsonify({"message": "name 必填"}), 400

    existed = Tag.query.filter(Tag.name.ilike(name)).first()
    if existed:
        return jsonify({
            "tag_id": existed.tag_id,
            "name": existed.name
        }), 200

    tag = Tag(name=name, created_by=user_id)
    db.session.add(tag)
    db.session.commit()

    return jsonify({
        "tag_id": tag.tag_id,
        "name": tag.name
    }), 201


@tag_bp.route("/content/<int:content_id>", methods=["POST"])
@jwt_required()
def add_tags_to_content(content_id):
    user_id = get_jwt_identity()
    try:
        user_id = int(user_id)
    except Exception:
        pass
    data = request.get_json() or {}
    names = data.get("tags") or []

    content = Content.query.get(content_id)
    if not content:
        return jsonify({"message": "content 不存在"}), 404

    if not _user_in_project(user_id, content.project_id):
        return jsonify({"message": "你沒有這個專案的權限"}), 403

    if not isinstance(names, list) or len(names) == 0:
        return jsonify({"message": "tags 必須是非空的陣列"}), 400

    attached = []
    for raw_name in names:
        name = (raw_name or "").strip()
        if not name:
            continue

        tag = Tag.query.filter(Tag.name.ilike(name)).first()
        if not tag:
            tag = Tag(name=name, created_by=user_id)
            db.session.add(tag)
            db.session.flush()

        exists_ct = ContentTag.query.filter_by(
            content_id=content_id,
            tag_id=tag.tag_id
        ).first()
        if not exists_ct:
            ct = ContentTag(content_id=content_id, tag_id=tag.tag_id)
            db.session.add(ct)

        attached.append({
            "tag_id": tag.tag_id,
            "name": tag.name
        })

    db.session.commit()

    return jsonify({
        "content_id": content_id,
        "tags": attached
    }), 200


@tag_bp.route("/content/<int:content_id>", methods=["GET"])
@jwt_required()
def list_content_tags(content_id):
    user_id = get_jwt_identity()
    try:
        user_id = int(user_id)
    except Exception:
        pass
    content = Content.query.get(content_id)

    if not content:
        return jsonify({"message": "content 不存在"}), 404

    if not _user_in_project(user_id, content.project_id):
        return jsonify({"message": "你沒有這個專案的權限"}), 403

    # 使用 model 定義的關聯 .tags
    tags = content.tags

    result = [
        {"tag_id": t.tag_id, "name": t.name}
        for t in tags
    ]
    return jsonify(result), 200


@tag_bp.route("/<int:tag_id>/contents", methods=["GET"])
@jwt_required()
def list_contents_by_tag(tag_id):
    tag = Tag.query.get(tag_id)
    if not tag:
        return jsonify({"message": "tag 不存在"}), 404

    # 使用 model 定義的關聯 .contents
    cts = tag.contents

    result = []
    for c in cts:
        result.append({
            "content_id": c.content_id,
            "title": c.title,
            "project_id": c.project_id,
        })

    return jsonify({
        "tag_id": tag.tag_id,
        "tag_name": tag.name,
        "contents": result
    }), 200