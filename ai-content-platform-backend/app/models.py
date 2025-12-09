from datetime import datetime
from .extensions import db 

# ======================
# User
# ======================
class User(db.Model):
    __tablename__ = "user"

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ======================
# Project
# ======================
class Project(db.Model):
    __tablename__ = "project"

    project_id = db.Column(db.Integer, primary_key=True) # 注意：這裡用的是 project_id
    id = db.synonym('project_id') # 方便程式用 .id 存取
    
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("user.user_id"),
        nullable=False,
    )

    owner = db.relationship("User", backref=db.backref("projects", lazy=True))


# ======================
# ProjectMember
# ======================
class ProjectMember(db.Model):
    __tablename__ = "project_member"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(
        db.Integer,
        db.ForeignKey("project.project_id"),
        nullable=False,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.user_id"),
        nullable=False,
    )
    role = db.Column(db.String(20), nullable=False)  
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    project = db.relationship("Project", backref="members")
    user = db.relationship("User", backref="project_memberships")


# ======================
# ContentTag (關聯表)
# ======================
class ContentTag(db.Model):
    __tablename__ = "content_tag"

    content_id = db.Column(
        db.Integer,
        db.ForeignKey("content.content_id"),
        primary_key=True,
    )
    tag_id = db.Column(
        db.Integer,
        db.ForeignKey("tag.tag_id"),
        primary_key=True,
    )


# ======================
# Tag
# ======================
class Tag(db.Model):
    __tablename__ = "tag"

    tag_id = db.Column(db.Integer, primary_key=True)
    id = db.synonym('tag_id')
    
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("user.user_id"))

    creator = db.relationship("User", backref="tags")
    
    contents = db.relationship(
        "Content",
        secondary="content_tag",
        back_populates="tags",
        lazy="select",
    )


# ======================
# Content (簡化版：直接存內容)
# ======================
class Content(db.Model):
    __tablename__ = "content"

    content_id = db.Column(db.Integer, primary_key=True)
    id = db.synonym('content_id') # 方便程式用 .id 存取

    project_id = db.Column(
        db.Integer,
        db.ForeignKey("project.project_id"),
        nullable=False,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.user_id"),
    )
    
    title = db.Column(db.String(255), nullable=False)
    primary_type = db.Column(db.String(30), default="text")
    source_tool = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 🚨 關鍵修改：直接在 Content 表存 Prompt 和 Response
    # 這是 MVP 最穩定的做法，先把功能跑通再說
    original_prompt = db.Column(db.Text) 
    generated_content = db.Column(db.Text) 
    
    # 為了配合 content_routes.py，我們加上這兩個別名 (property)
    @property
    def prompt(self):
        return self.original_prompt
    
    @prompt.setter
    def prompt(self, value):
        self.original_prompt = value

    @property
    def response(self):
        return self.generated_content
    
    @response.setter
    def response(self, value):
        self.generated_content = value

    # 關聯
    project = db.relationship("Project", backref="contents")
    creator = db.relationship("User", backref="created_contents")
    
    tags = db.relationship(
        "Tag",
        secondary="content_tag",
        back_populates="contents",
        lazy="select",
    )


# ======================
# ContentVersion (保留但不強制使用)
# ======================
class ContentVersion(db.Model):
    __tablename__ = "content_version"

    version_id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey("content.content_id"), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    version_number = db.Column(db.Integer, nullable=False)
    
    prompt = db.Column(db.Text)
    response = db.Column(db.Text) # 補上這個欄位
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    content = db.relationship("Content", backref="versions")