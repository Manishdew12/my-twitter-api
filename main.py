from fastapi import FastAPI, HTTPException
from twikit import Client
import asyncio
import os

app = FastAPI()

# --- CONFIGURATION (Load from Environment Variables) ---
USERNAME = os.getenv("TWITTER_USERNAME")
EMAIL = os.getenv("TWITTER_EMAIL")
PASSWORD = os.getenv("TWITTER_PASSWORD")

# Cookies path (Persistent Volume ke liye)
COOKIES_PATH = "/app/data/cookies.json"

client = Client('en-US')

async def init_client():
    # Folder check karein, agar nahi hai toh banayein
    os.makedirs(os.path.dirname(COOKIES_PATH), exist_ok=True)

    if os.path.exists(COOKIES_PATH):
        try:
            client.load_cookies(COOKIES_PATH)
            print(f"✅ Cookies loaded from {COOKIES_PATH}")
        except Exception as e:
            print(f"⚠️ Cookie load failed, trying fresh login: {e}")
            await perform_login()
    else:
        await perform_login()

async def perform_login():
    print("🔄 Logging in...")
    try:
        await client.login(
            auth_info_1=USERNAME,
            auth_info_2=EMAIL,
            password=PASSWORD
        )
        client.save_cookies(COOKIES_PATH)
        print("✅ Logged in & Cookies saved!")
    except Exception as e:
        print(f"❌ Login Failed: {e}")

@app.on_event("startup")
async def startup_event():
    await init_client()

@app.get("/get_tweets")
async def get_tweets(username: str):
    try:
        user = await client.get_user_by_screen_name(username)
        tweets = await user.get_tweets('Tweets', count=5)
        
        results = []
        for tweet in tweets:
            media_urls = [m['media_url_https'] for m in tweet.media] if tweet.media else []
            
            results.append({
                "id": tweet.id,
                "text": tweet.full_text,
                "created_at": tweet.created_at,
                "media": media_urls,
                "url": f"https://x.com/{username}/status/{tweet.id}",
                "user": {"name": user.name, "username": user.screen_name}
            })
            
        return {"success": True, "tweets": results}

    except Exception as e:
        return {"success": False, "error": str(e)}
