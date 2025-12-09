import os
import json
import google.generativeai as genai
from flask import current_app

# ==========================================
# 🔧 輔助函式：取得模型實例 (支援動態切換)
# ==========================================
def get_model(model_name=None):
    """
    取得 Gemini 模型
    model_name: 前端傳來的模型名稱 (例如 'gemini-pro', 'gemini-1.5-flash')
    """
    api_key = current_app.config.get("GEMINI_API_KEY")
    
    if not api_key:
        print("⚠️ 錯誤：未設定 GEMINI_API_KEY")
        return None

    try:
        genai.configure(api_key=api_key)
        
        # 🚨 關鍵修復：如果有傳入 model_name 就用傳入的，否則預設 gemini-1.5-flash
        target_model = model_name if model_name else "gemini-1.5-flash"
        
        print(f"🤖 正在啟動模型: {target_model}") # Debug 用，讓你從終端機看到現在用哪顆

        return genai.GenerativeModel(
            model_name=target_model,
            generation_config={
                "temperature": 0.7,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 2048,
            }
        )
    except Exception as e:
        print(f"❌ AI Config Error: {e}")
        return None

# ==========================================
# 1. 通用生成 (Chat / Q&A)
# ==========================================
def generate_ai_content(prompt, model_name=None):
    # ✨ 這裡要接收 model_name 並傳給 get_model
    model = get_model(model_name)
    if not model: return "系統未設定 AI 金鑰。"
    
    # 強制中文指令
    system_instruction = f"""
    你是一個繁體中文的 AI 助手。
    請**一律使用繁體中文 (Traditional Chinese, Taiwan)** 回答以下問題。
    如果內容涉及程式碼，請保留程式碼原樣，但解釋說明的部分請用繁體中文。
    
    問題：
    {prompt}
    """

    try:
        response = model.generate_content(system_instruction)
        return response.text
    except Exception as e:
        return f"AI 生成失敗 ({model_name}): {str(e)}"

# ==========================================
# 2. 場景 1：懶人救星 - 自動生成標籤
# ==========================================
def generate_tags_from_text(text, model_name=None):
    # ✨ 這裡也要傳
    model = get_model(model_name)
    if not model: return []
    
    safe_text = text[:1000]

    prompt = f"""
    請閱讀以下筆記，提取 3-5 個關鍵字作為標籤。
    規則：
    1. 只回傳純 JSON 陣列 (Array of Strings)。
    2. 不要包含 Markdown (如 ```json)。
    3. **標籤請一律使用繁體中文或英文術語，禁止使用日文或簡體中文。**
    
    筆記：
    {safe_text}
    """
    
    try:
        response = model.generate_content(prompt)
        cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
        tags_list = json.loads(cleaned_text)
        return tags_list if isinstance(tags_list, list) else []
    except Exception as e:
        print(f"❌ Auto-Tag Error: {e}")
        return []

# ==========================================
# 3. 場景 2：筆記整理師 - 一鍵優化
# ==========================================
def refine_text_content(text, model_name=None):
    # ✨ 這裡也要傳
    model = get_model(model_name)
    if not model: return text
    
    prompt = f"""
    你是一位專業的台灣技術文件編輯。請優化以下筆記：
    要求：
    1. **請使用流暢的繁體中文 (Traditional Chinese)。**
    2. 修正錯字、標點符號。
    3. 使用 Markdown 排版。
    4. 直接回傳內容，不要有開場白。
    
    原始筆記：
    {text}
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return text

# ==========================================
# 4. 場景 3：專案總結報告
# ==========================================
def summarize_project_notes(notes_list, model_name=None):
    # ✨ 這裡也要傳
    model = get_model(model_name)
    if not model: return "無法生成報告"
    if not notes_list: return "資料不足。"

    combined_text = "\n\n".join([f"[{n['date']}] {n['content']}" for n in notes_list])
    
    prompt = f"""
    你是一個台灣的專案經理。請根據以下筆記寫一份「專案進度週報」。
    格式：## 本週進度, ### 已完成, ### 問題, ### 待辦。
    語言：**全篇請務必使用繁體中文 (Traditional Chinese)。**
    
    資料：
    {combined_text[:4000]}
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"報告生成失敗: {str(e)}"