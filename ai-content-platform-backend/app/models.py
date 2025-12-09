from datetime import datetime
from .extensions import db 

# ======================
# User & Project (保持不變)
# ======================
class User(db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Project(db.Model):
    __tablename__ = "project"
    project_id = db.Column(db.Integer, primary_key=True)
    id = db.synonym('project_id')
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    owner = db.relationship("User", backref=db.backref("projects", lazy=True))

class ProjectMember(db.Model):
    __tablename__ = "project_member"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.project_id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    role = db.Column(db.String(20), nullable=False)  
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    project = db.relationship("Project", backref="members")
    user = db.relationship("User", backref="project_memberships")

# ======================
# Tag & ContentTag (保持不變)
# ======================
class ContentTag(db.Model):
    __tablename__ = "content_tag"
    content_id = db.Column(db.Integer, db.ForeignKey("content.content_id"), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey("tag.tag_id"), primary_key=True)

class Tag(db.Model):
    __tablename__ = "tag"
    tag_id = db.Column(db.Integer, primary_key=True)
    id = db.synonym('tag_id')
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    creator = db.relationship("User", backref="tags")
    contents = db.relationship("Content", secondary="content_tag", back_populates="tags", lazy="select")

# ======================
# Content (外殼) - 🚀 核心修改
# ======================
class Content(db.Model):
    __tablename__ = "content"
    content_id = db.Column(db.Integer, primary_key=True)
    id = db.synonym('content_id')

    project_id = db.Column(db.Integer, db.ForeignKey("project.project_id"), nullable=False)
    creator_user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    
    # 🔗 關鍵：指向最新版本的指針 (nullable=True 很重要，防止建立時死鎖)
    latest_version_id = db.Column(db.Integer, db.ForeignKey("content_version.version_id"), nullable=True)

    title = db.Column(db.String(255), nullable=False)
    primary_type = db.Column(db.String(30), default="text")
    source_tool = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 為了讓 search_routes.py 能繼續運作，我們使用 property 代理最新版本的內容
    @property
    def prompt(self):
        return self.latest_version.prompt if self.latest_version else ""
    
    @property
    def response(self):
        return self.latest_version.response if self.latest_version else ""

    # 關聯
    project = db.relationship("Project", backref="contents")
    creator = db.relationship("User", backref="created_contents")
    
    tags = db.relationship("Tag", secondary="content_tag", back_populates="contents", lazy="select")

    # 定義與 Version 的關係 (1對多)
    versions = db.relationship(
        "ContentVersion",
        back_populates="content",
        foreign_keys="ContentVersion.content_id", 
        cascade="all, delete-orphan"
    )
    
    # 定義與 Latest Version 的關係 (1對1)
    latest_version = db.relationship(
        "ContentVersion",
        foreign_keys=[latest_version_id],
        uselist=False,
        post_update=True # 🚀 允許先建立 Content 再回頭更新 ID
    )

# ======================
# ContentVersion (核心資料) - 🚀 核心修改
# ======================
class ContentVersion(db.Model):
    __tablename__ = "content_version"

    version_id = db.Column(db.Integer, primary_key=True)
    
    content_id = db.Column(db.Integer, db.ForeignKey("content.content_id"), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    
    version_number = db.Column(db.Integer, nullable=False)
    
    # 這裡存實際資料 (prompt & response)
    prompt = db.Column(db.Text)
    response = db.Column(db.Text) 
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 反向關聯
    content = db.relationship(
        "Content", 
        back_populates="versions",
        foreign_keys=[content_id]
    )