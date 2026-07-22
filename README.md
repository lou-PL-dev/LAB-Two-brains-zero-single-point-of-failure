# News Summarizer

> 📋 **Reviewer?** Start with [`lab_proof.md`](./lab_proof.md) for setup verification, checkpoints, and screenshots.

Multi-provider news summarization app: fetches articles, summarizes them with OpenAI, and analyzes sentiment with Cohere. Includes fallback logic, cost tracking, sync/async processing, local caching, keyword search, and a web UI.

## What it does

- Fetches top headlines from NewsAPI by category, or searches by free-text keyword
- Summarizes each article using OpenAI (gpt-4o-mini)
- Analyzes sentiment using Cohere (command-r-plus)
- Falls back gracefully if a provider fails
- Caches processed articles locally to avoid paying twice for the same one
- Tracks and reports API costs per run

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file (see `.env.example`) with your own keys:

OPENAI_API_KEY=your_key
COHERE_API_KEY=your_key
NEWS_API_KEY=your_key

Validate your config:

```bash
python config.py
```

## Usage

Interactive terminal app:
```bash
python main.py
```

Run the summarizer directly:
```bash
python summarizer.py --sync   # sequential processing
python summarizer.py --async  # concurrent processing (faster, same cost)
```

Web UI:
```bash
python app.py
```
Then open http://127.0.0.1:5000. Choose a fixed category, or search by keyword for more granular topics (e.g. "artificial intelligence" instead of just "technology"). Each field has an inline help icon (i) explaining how to get the most relevant results.

Run tests:
```bash
pytest test_summarizer.py -v
```

## Example output

1. Fourth person dies from Legionnaires' disease outbreak in Manhattan
Summary: A fourth individual has succumbed to Legionnaires' disease...
Sentiment: The text conveys a negative sentiment...
Link: https://...

## Cost analysis

- ~$0.0001–0.0002 per article (OpenAI summary + Cohere sentiment combined)
- Example run: 4 articles processed for $0.0005 total (8 API calls)
- Cost scales linearly with number of articles; async mode is faster but costs the same as sync
- Cached articles cost nothing to reprocess

## Known limitations

- **Keyword search window**: results are limited to the last 7 days. The free NewsAPI plan doesn't reliably index same-day articles, so this window balances freshness with availability — very recent stories may occasionally be missed.
- **Sentiment analysis**: currently returns a single-label judgment (positive/neutral/negative) with a one-line explanation. It doesn't capture mixed sentiment, sarcasm, or topic-specific nuance — an area with room for ongoing refinement rather than a fixed target.