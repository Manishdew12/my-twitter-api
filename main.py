from fastapi import FastAPI, HTTPException
from ntscraper import Nitter
import uvicorn
import random

app = FastAPI()

# ⚠️ CHANGE: Auto-search band kar diya. 
# Hum seedha ek specific instance use karenge.
# Agar ye block ho jaye, to ise badalkar 'https://nitter.cz' ya 'https://nitter.net' kar dena.
scraper = Nitter(log_level=1)

@app.get("/")
def home():
    return {"status": "Twitter Scraper API is Running (Forced Mode) 🚀"}

@app.get("/tweets")
def get_tweets(user: str):
    try:
        print(f"Fetching tweets for: {user}")
        
        # ⚠️ Force specific instance here
        # Ye line ensure karti hai ki hum random search na karein
        data = scraper.get_tweets(user, mode='user', number=5, instance="https://nitter.privacyredirect.com")
        
        if not data or 'tweets' not in data:
             # Fallback: Agar upar wala fail ho, to nitter.cz try karo
             print("Primary instance failed, trying backup...")
             data = scraper.get_tweets(user, mode='user', number=5, instance="https://nitter.cz")

        if not data or 'tweets' not in data:
            return {"error": "No tweets found or User blocked"}

        clean_tweets = []
        for tweet in data['tweets']:
            if tweet['is-retweet'] is False:
                clean_tweets.append({
                    "tweet_id": tweet['link'].split('/')[-1],
                    "text": tweet['text'],
                    "date": tweet['date'],
                    "images": tweet['pictures'],
                    "url": tweet['link']
                })
        
        return clean_tweets

    except Exception as e:
        print(f"Error: {e}")
        # Error 500 ki jagah detail dikhaye
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
