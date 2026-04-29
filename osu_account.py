from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import requests
import os
from dotenv import load_dotenv
from pathlib import Path

# 1. 設定絕對路徑
BASE_DIR = Path(__file__).resolve().parent

# 2. 載入 .env 裡的機密資訊
load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
OSU_USER_ID = os.getenv("OSU_USER_ID")

# 3. 網頁首頁
@app.get("/")
def serve_webpage():
    html_path = BASE_DIR / "index.html"
    return FileResponse(html_path)

# 4. API 介面：支援 mode 參數切換模式
@app.get("/api/my-osu-data")
def get_osu_data(mode: str = Query("osu")):
    # 驗證模式，防止輸入錯誤導致 API 噴錯
    valid_modes = ["osu", "taiko", "fruits", "mania"]
    if mode not in valid_modes:
        mode = "osu"

    # 先向 osu! 換取「通行證」(Access Token)
    token_url = "https://osu.ppy.sh/oauth/token"
    token_data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
        "scope": "public"
    }
    
    try:
        token_response = requests.post(token_url, data=token_data).json()
        access_token = token_response.get("access_token")

        # 拿著通行證，去抓取指定模式 (mode) 的資料
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # 這裡的網址最後一個段落就是模式：/osu, /taiko, /fruits, 或 /mania
        user_url = f"https://osu.ppy.sh/api/v2/users/{OSU_USER_ID}/{mode}"
        user_response = requests.get(user_url, headers=headers)

        return user_response.json()
        
    except Exception as e:
        return {"error": str(e)}
