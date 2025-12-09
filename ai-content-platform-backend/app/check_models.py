# check_models.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ 找不到 API Key，請檢查 .env 檔案")
else:
    genai.configure(api_key=api_key)
    print(f"🔑 使用 Key: {api_key[:5]}... 正在查詢可用模型...\n")
    
    try:
        print("=== 你的帳號可用的生成模型 ===")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
        print("================================")
    except Exception as e:
        print(f"❌ 查詢失敗: {e}")

