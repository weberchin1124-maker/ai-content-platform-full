# app/schemas.py

from marshmallow import Schema, fields, validate

# ======================
# Tag Schema
# 用於回傳（Dump）時顯示單一標籤資訊
# ======================
class TagSchema(Schema):
    """用於序列化 Tag 模型的回傳 Schema"""
    id = fields.Int(dump_only=True)   # 注意：資料庫模型通常是 id，不是 tag_id
    name = fields.Str(dump_only=True)

# ======================
# 內容相關 Schema
# ======================

class ContentCreationSchema(Schema):
    """用於驗證 POST /api/contents/project/<id> 請求的輸入資料"""
    
    # 1. 核心內容欄位
    # title: 必填
    title = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    
    # primary_type: 非必填，預設為 "text" (避免前端忘記傳就報錯)
    primary_type = fields.Str(
        required=False, 
        missing="text",
        validate=validate.OneOf(["text", "image", "code", "audio", "video"])
    )
    
    # source_tool: 非必填，預設為 Unknown
    source_tool = fields.Str(required=False, missing="Unknown")
    
    # prompt: 必填 (這是最重要的內容)
    prompt = fields.Str(required=True)
    
    # response: 非必填，預設為空字串 (配合前端傳來的欄位名 'response')
    response = fields.Str(required=False, missing="") 

    # 2. 標籤欄位
    # 🚨 關鍵修改：欄位名稱改成 'tags' 以配合前端
    # 接收格式範例: ["Python", "Notes"]
    tags = fields.List(
        fields.Str(
            validate=validate.Length(min=1, max=50) # 限制每個標籤的字數
        ),
        required=False,     
        missing=[],         
        validate=validate.Length(max=10) # 限制一次最多只能傳 10 個標籤
    )


class ContentResponseSchema(Schema):
    """用於序列化 GET 請求回傳給前端的 Content 資料"""
    
    id = fields.Int(dump_only=True)
    project_id = fields.Int(dump_only=True)
    title = fields.Str(dump_only=True)
    primary_type = fields.Str(dump_only=True)
    
    # 對應資料庫欄位名稱
    original_prompt = fields.Str(dump_only=True) 
    generated_content = fields.Str(dump_only=True)
    
    created_at = fields.DateTime(dump_only=True)
    
    # ✅ 巢狀回傳標籤物件列表
    tags = fields.List(fields.Nested(TagSchema), dump_only=True)