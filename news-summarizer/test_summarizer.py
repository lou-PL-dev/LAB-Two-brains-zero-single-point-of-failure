"""
test_summarizer.py
Unit tests for the news summarizer app.
Uses mocking to avoid real API calls (no cost, no network needed).
"""

import pytest
from unittest.mock import MagicMock, patch

from config import Config
from summarizer import NewsSummarizer
from llm_providers import CostTracker


@pytest.fixture
def mock_config():
    """Provides a fake config so tests don't need real API keys."""
    config = MagicMock(spec=Config)
    config.openai_api_key = "fake-openai-key"
    config.cohere_api_key = "fake-cohere-key"
    config.news_api_key = "fake-news-key"
    config.max_retries = 3
    config.request_timeout = 30
    return config


@pytest.fixture
def sample_articles():
    """Sample article data, shaped like NewsAPIClient.fetch_articles() output."""
    return [
        {
            "title": "Test Article One",
            "description": "A description of test article one.",
            "url": "https://example.com/1",
            "source": "Example News",
        },
        {
            "title": "Test Article Two",
            "description": "A description of test article two.",
            "url": "https://example.com/2",
            "source": "Example News",
        },
    ]


class TestNewsSummarizer:
    """Tests for the sync NewsSummarizer class."""

    @patch("summarizer.NewsAPIClient")
    @patch("summarizer.LLMProviders")
    def test_process_articles_success(self, mock_llm_class, mock_news_class, mock_config, sample_articles):
        """When both providers succeed, results should contain real summary and sentiment."""
        mock_news_class.return_value.fetch_articles.return_value = sample_articles

        mock_llm = mock_llm_class.return_value
        mock_llm.summarize_with_openai.return_value = "A concise summary."
        mock_llm.analyze_sentiment_with_cohere.return_value = "Positive sentiment."

        summarizer = NewsSummarizer(mock_config)
        results = summarizer.process_articles(num_articles=2)

        assert len(results) == 2
        assert results[0]["summary"] == "A concise summary."
        assert results[0]["sentiment"] == "Positive sentiment."
        assert results[0]["title"] == "Test Article One"

    @patch("summarizer.NewsAPIClient")
    @patch("summarizer.LLMProviders")
    def test_openai_fallback_on_failure(self, mock_llm_class, mock_news_class, mock_config, sample_articles):
        """When OpenAI fails (returns None), fallback to the article's raw description."""
        mock_news_class.return_value.fetch_articles.return_value = sample_articles

        mock_llm = mock_llm_class.return_value
        mock_llm.summarize_with_openai.return_value = None
        mock_llm.analyze_sentiment_with_cohere.return_value = "Positive sentiment."

        summarizer = NewsSummarizer(mock_config)
        results = summarizer.process_articles(num_articles=2)

        assert results[0]["summary"] == "A description of test article one."

    @patch("summarizer.NewsAPIClient")
    @patch("summarizer.LLMProviders")
    def test_cohere_fallback_on_failure(self, mock_llm_class, mock_news_class, mock_config, sample_articles):
        """When Cohere fails (returns None), fallback to a default sentiment message."""
        mock_news_class.return_value.fetch_articles.return_value = sample_articles

        mock_llm = mock_llm_class.return_value
        mock_llm.summarize_with_openai.return_value = "A concise summary."
        mock_llm.analyze_sentiment_with_cohere.return_value = None

        summarizer = NewsSummarizer(mock_config)
        results = summarizer.process_articles(num_articles=2)

        assert results[0]["sentiment"] == "Sentiment unavailable."

    @patch("summarizer.NewsAPIClient")
    @patch("summarizer.LLMProviders")
    def test_empty_articles_list(self, mock_llm_class, mock_news_class, mock_config):
        """When the News API returns no articles, results should be an empty list."""
        mock_news_class.return_value.fetch_articles.return_value = []

        summarizer = NewsSummarizer(mock_config)
        results = summarizer.process_articles(num_articles=2)

        assert results == []


class TestCostTracker:
    """Tests for the CostTracker used across providers."""

    def test_add_cost_openai(self):
        tracker = CostTracker()
        cost = tracker.add("openai", input_tokens=1000, output_tokens=1000)

        assert cost == pytest.approx(0.002)  # 0.0005 + 0.0015
        assert tracker.total_cost == pytest.approx(0.002)
        assert len(tracker.calls) == 1

    def test_add_cost_accumulates(self):
        tracker = CostTracker()
        tracker.add("openai", input_tokens=1000, output_tokens=0)
        tracker.add("cohere", input_tokens=1000, output_tokens=0)

        assert len(tracker.calls) == 2
        assert tracker.total_cost > 0

    def test_summary_format(self):
        tracker = CostTracker()
        tracker.add("openai", input_tokens=500, output_tokens=500)

        summary = tracker.summary()
        assert "Total spent" in summary
        assert "1 calls" in summary