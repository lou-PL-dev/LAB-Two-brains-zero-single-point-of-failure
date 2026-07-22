"""
summarizer.py
Core logic: fetches articles, summarizes them with OpenAI,
and analyzes sentiment with Cohere. Sync and async versions available.
Tracks costs along the way. Uses a local cache to avoid reprocessing
identical articles and save money. Supports fetching by category or by keyword.

Usage:
    python summarizer.py --sync
    python summarizer.py --async
"""

import argparse
import asyncio
from openai import AsyncOpenAI
import cohere

from config import Config
from news_api import NewsAPIClient
from llm_providers import LLMProviders, CostTracker
from cache import get_cached, set_cached


class NewsSummarizer:
    """Orchestrates fetching, summarizing, and sentiment analysis of news articles (sync)."""

    def __init__(self, config: Config):
        self.config = config
        self.cost_tracker = CostTracker()
        self.news_client = NewsAPIClient(config)
        self.llm = LLMProviders(config, self.cost_tracker)

    def _summarize_and_cache(self, article):
        """Summarizes + analyzes sentiment for one article, using cache when available."""
        source_text = f"{article['title']}. {article['description'] or ''}"

        cached = get_cached(source_text)
        if cached:
            summary, sentiment = cached["summary"], cached["sentiment"]
        else:
            summary = self.llm.summarize_with_openai(source_text)
            if summary is None:
                summary = article["description"] or "Summary unavailable."

            sentiment = self.llm.analyze_sentiment_with_cohere(source_text)
            if sentiment is None:
                sentiment = "Sentiment unavailable."

            set_cached(source_text, summary, sentiment)

        return {
            "title": article["title"],
            "url": article["url"],
            "source": article["source"],
            "summary": summary,
            "sentiment": sentiment,
        }

    def process_articles(self, category="technology", country="us", num_articles=2):
        """Fetches by category (top-headlines) and processes each article."""
        articles = self.news_client.fetch_articles(
            category=category, country=country, page_size=num_articles
        )
        return [self._summarize_and_cache(article) for article in articles]

    def process_by_keyword(self, keyword, num_articles=3, from_date=None):
        """Fetches by keyword (everything endpoint) and processes each article."""
        articles = self.news_client.search_articles(
            keyword, page_size=num_articles, from_date=from_date
        )
        return [self._summarize_and_cache(article) for article in articles]

    def print_report(self, results):
        print("\n" + "=" * 60)
        print("NEWS SUMMARY REPORT (SYNC)")
        print("=" * 60)

        for i, item in enumerate(results, 1):
            print(f"\n{i}. {item['title']} ({item['source']})")
            print(f"   Summary: {item['summary']}")
            print(f"   Sentiment: {item['sentiment']}")
            print(f"   Link: {item['url']}")

        print("\n" + "-" * 60)
        print(self.cost_tracker.summary())
        print("-" * 60)


class AsyncNewsSummarizer:
    """Async version of NewsSummarizer for concurrent processing of articles."""

    def __init__(self, config: Config):
        self.config = config
        self.cost_tracker = CostTracker()
        self.news_client = NewsAPIClient(config)
        self.async_openai = AsyncOpenAI(api_key=config.openai_api_key)
        self.async_cohere = cohere.AsyncClientV2(api_key=config.cohere_api_key)

    async def summarize_with_openai_async(self, text, model="gpt-4o-mini"):
        for attempt in range(self.config.max_retries):
            try:
                response = await self.async_openai.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "Summarize the article in 2 sentences."},
                        {"role": "user", "content": text},
                    ],
                    max_tokens=150,
                )
                usage = response.usage
                self.cost_tracker.add("openai", usage.prompt_tokens, usage.completion_tokens)
                return response.choices[0].message.content
            except Exception as e:
                print(f"OpenAI async attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(1)
        return None

    async def analyze_sentiment_with_cohere_async(self, text, model="command-r-plus-08-2024"):
        for attempt in range(self.config.max_retries):
            try:
                response = await self.async_cohere.chat(
                    model=model,
                    messages=[
                        {
                            "role": "user",
                            "content": f"Classify the sentiment (positive/neutral/negative) of this text in one short sentence:\n\n{text}",
                        }
                    ],
                )
                usage = response.usage
                input_tokens = usage.tokens.input_tokens if usage and usage.tokens else 0
                output_tokens = usage.tokens.output_tokens if usage and usage.tokens else 0
                self.cost_tracker.add("cohere", input_tokens, output_tokens)
                return response.message.content[0].text
            except Exception as e:
                print(f"Cohere async attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(1)
        return None

    async def process_one_article(self, article):
        source_text = f"{article['title']}. {article['description'] or ''}"

        cached = get_cached(source_text)
        if cached:
            return {
                "title": article["title"],
                "url": article["url"],
                "source": article["source"],
                "summary": cached["summary"],
                "sentiment": cached["sentiment"],
            }

        summary_task = self.summarize_with_openai_async(source_text)
        sentiment_task = self.analyze_sentiment_with_cohere_async(source_text)

        summary, sentiment = await asyncio.gather(summary_task, sentiment_task)

        if summary is None:
            summary = article["description"] or "Summary unavailable."
        if sentiment is None:
            sentiment = "Sentiment unavailable."

        set_cached(source_text, summary, sentiment)

        return {
            "title": article["title"],
            "url": article["url"],
            "source": article["source"],
            "summary": summary,
            "sentiment": sentiment,
        }

    async def process_articles_async(self, category="technology", country="us", num_articles=2):
        articles = self.news_client.fetch_articles(
            category=category, country=country, page_size=num_articles
        )

        tasks = [self.process_one_article(article) for article in articles]
        results = await asyncio.gather(*tasks)
        return results

    def print_report(self, results):
        print("\n" + "=" * 60)
        print("NEWS SUMMARY REPORT (ASYNC)")
        print("=" * 60)

        for i, item in enumerate(results, 1):
            print(f"\n{i}. {item['title']} ({item['source']})")
            print(f"   Summary: {item['summary']}")
            print(f"   Sentiment: {item['sentiment']}")
            print(f"   Link: {item['url']}")

        print("\n" + "-" * 60)
        print(self.cost_tracker.summary())
        print("-" * 60)


async def main_async():
    config = Config()
    async_summarizer = AsyncNewsSummarizer(config)

    results = await async_summarizer.process_articles_async(num_articles=2)
    async_summarizer.print_report(results)


def main_sync():
    config = Config()
    summarizer = NewsSummarizer(config)

    results = summarizer.process_articles(num_articles=2)
    summarizer.print_report(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the news summarizer in sync or async mode.")
    parser.add_argument("--async", dest="run_async", action="store_true", help="Run the async (concurrent) version.")
    parser.add_argument("--sync", dest="run_sync", action="store_true", help="Run the sync (sequential) version.")
    args = parser.parse_args()

    if args.run_async and args.run_sync:
        print("Choose only one: --sync or --async, not both.")
    elif args.run_async:
        asyncio.run(main_async())
    elif args.run_sync:
        main_sync()
    else:
        print("Please specify a mode: --sync or --async")