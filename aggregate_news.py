import feedparser
import requests
import json
import os
import re  # <-- Used to strip HTML tags
from datetime import datetime

# --- THE SANITIZER FUNCTION ---
def clean_summary(raw_text, max_length=200):
    if not raw_text:
        return "No intel summary available."
    
    # 1. Strip all HTML tags (like <p>, <a>, <img>)
    text_no_html = re.sub(r'<[^>]+>', '', raw_text)
    
    # 2. Clean up weird spacing and newlines
    clean_text = " ".join(text_no_html.split())
    
    # 3. Truncate cleanly so it doesn't cut a word in half
    if len(clean_text) > max_length:
        return clean_text[:max_length].rsplit(' ', 1)[0] + '...'
        
    return clean_text
# ------------------------------

# 1. High-Trust AI RSS Feeds (The Snipers)
RSS_FEEDS = [
    "https://bair.berkeley.edu/blog/feed.xml", # Berkeley AI Research
    "https://research.google/blog/rss",        # Google Research
    "https://machinelearningmastery.com/blog/feed/" # ML Mastery
]

# 2. Real-Time API (The Radar)
# Searching specifically for AI, Machine Learning, or LLM breakthroughs
GNEWS_API_KEY = os.environ.get("GNEWS_API_KEY")
GNEWS_URL = f"https://gnews.io/api/v4/search?q=\"artificial intelligence\" OR \"machine learning\" OR \"LLM\"&lang=en&max=10&apikey={GNEWS_API_KEY}"

articles_list = []

# --- FETCH RSS FEEDS ---
for url in RSS_FEEDS:
    try:
        feed = feedparser.parse(url)
        # Clean up the source name for the UI
        source_name = url.split("//")[1].split("/")[0].replace("www.", "").split(".")[0]
        
        for entry in feed.entries[:5]: 
            # Grab the raw description
            raw_desc = getattr(entry, 'summary', getattr(entry, 'description', ''))
            
            # Sanitize and truncate it!
            clean_desc = clean_summary(raw_desc)
            
            articles_list.append({
                "title": entry.title,
                "description": f"[{source_name.upper()}] {clean_desc}", 
                "url": entry.link,
                "published_raw": getattr(entry, 'published', datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
            })
    except Exception as e:
        print(f"Error fetching {url}: {e}")

# --- FETCH GNEWS API ---
if GNEWS_API_KEY:
    try:
        response = requests.get(GNEWS_URL)
        if response.status_code == 200:
            api_data = response.json().get("articles", [])
            for art in api_data:
                # Grab the raw API description
                raw_desc = art.get('description', '')
                
                # Sanitize and truncate it!
                clean_desc = clean_summary(raw_desc)
                
                articles_list.append({
                    "title": art["title"],
                    "description": f"[{art['source']['name'].upper()}] {clean_desc}",
                    "url": art["url"],
                    "published_raw": art["publishedAt"]
                })
    except Exception as e:
        print(f"API fetch failed: {e}")

# --- SORT & FORMAT FOR FRONTEND ---
# Sort by newest first
articles_list.sort(key=lambda x: x["published_raw"], reverse=True)

# Clean up the output so frontend only gets what it needs
for article in articles_list:
    article.pop("published_raw", None)

output_data = {
    "updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
    "news": articles_list
}

with open("data.json", "w") as f:
    json.dump(output_data, f, indent=4)

print(f"Pulse Protocol Updated: {len(articles_list)} AI signals intercepted and sanitized.")
