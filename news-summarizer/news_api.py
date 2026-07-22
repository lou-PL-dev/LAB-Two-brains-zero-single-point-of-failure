"""
news_api.py
Fetches news articles from NewsAPI.org
"""

import requests
from config import Config


class NewsAPIClient:
    """Client for fetching news articles from NewsAPI."""

    BASE_URL = "https://newsapi.org/v2/top-headlines"

    def __init__(self, config: Config):
        self.api_key = config.news_api_key
        self.timeout = config.request_timeout

    def fetch_articles(self, category="technology", country="us", page_size=3):
        """
        Fetches top headlines for a given category and country.

        Returns a list of dicts with title, description, url, source.
        """
        params = {
            "apiKey": self.api_key,
            "category": category,
            "country": country,
            "pageSize": page_size,
        }

        response = requests.get(self.BASE_URL, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()

        articles = []
        for item in data.get("articles", []):
            articles.append({
                "title": item.get("title"),
                "description": item.get("description"),
                "url": item.get("url"),
                "source": item.get("source", {}).get("name"),
            })

        return articles


if __name__ == "__main__":
    config = Config()
    client = NewsAPIClient(config)

    articles = client.fetch_articles()

    print(f"Fetched {len(articles)} articles:\n")
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title']} ({article['source']})")
        print(f"   {article['description']}\n")