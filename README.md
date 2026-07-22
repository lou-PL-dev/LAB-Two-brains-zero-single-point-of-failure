# News Summarizer

Multi-provider news summarization app: fetches articles, summarizes them with OpenAI, and analyzes sentiment with Cohere. Includes fallback logic, cost tracking, and both sync/async processing.

## What it does

- Fetches top headlines from NewsAPI by category
- Summarizes each article using OpenAI (gpt-4o-mini)
- Analyzes sentiment using Cohere (command-r-plus)
- Falls back gracefully if a provider fails
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

Interactive app:
```bash
python main.py
```

Run the summarizer directly:
```bash
python summarizer.py --sync   # sequential processing
python summarizer.py --async  # concurrent processing (faster, same cost)
```

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