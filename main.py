import os, requests, json
from datetime import datetime

# Focused on the 'Frontier' signal: Agentic AI, O1/O3 models, and hardware leaps
QUERY = '("agentic AI" OR "OpenAI" OR "LLM" OR "NVIDIA" OR "DeepSeek")'

def run():
    api_key = os.getenv('NEWS_API_KEY')
    # We use 'relevancy' here because AI news is high-volume; we want the big stories.
    url = f"https://newsapi.org/v2/everything?q={QUERY}&sortBy=relevancy&pageSize=10&language=en&apiKey={api_key}"
    
    response = requests.get(url).json()
    articles = response.get('articles', [])
    
    data = {
        "title": "Neural Pulse",
        "tagline": "The heartbeat of the AI frontier.",
        "updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "news": articles
    }
    
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    run()
