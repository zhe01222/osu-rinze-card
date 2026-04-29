from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles  # 1. 增加這一行
import requests
import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
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

# --- API 介面保持不變 ---
@app.get("/api/my-osu-data")
def get_osu_data(mode: str = Query("osu")):
    valid_modes = ["osu", "taiko", "fruits", "mania"]
    if mode not in valid_modes:
        mode = "osu"

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

        headers = {"Authorization": f"Bearer {access_token}"}
        user_url = f"https://osu.ppy.sh/api/v2/users/{OSU_USER_ID}/{mode}"
        user_response = requests.get(user_url, headers=headers)
        return user_response.json()
    except Exception as e:
        return {"error": str(e)}

# 2. 在程式碼最後面加入這行 (非常重要！)
# 這會讓 Render 幫你傳送影片、圖片、甚至是 HTML 本身
app.mount("/", StaticFiles(directory=BASE_DIR, html=True), name="static")
