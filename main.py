from fastapi import FastAPI, HTTPException
from ntscraper import Nitter
import uvicorn

app = FastAPI()
scraper = Nitter(log_level=1)

@app.get("/")
def home():
    return {"status": "Twitter Scraper API is Running 🚀"}

@app.get("/tweets")
def get_tweets(user: str):
    try:
        # Nitter se latest 5 tweets nikalo
        print(f"Fetching tweets for: {user}")
        data = scraper.get_tweets(user, mode='user', number=5)
        
        if not data or 'tweets' not in data:
            return {"error": "No tweets found or User blocked"}

        clean_tweets = []
        for tweet in data['tweets']:
            # Sirf woh tweets jisme text ya image ho
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
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
