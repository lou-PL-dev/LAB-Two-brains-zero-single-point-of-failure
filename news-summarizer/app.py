"""
app.py
Flask web UI for the news summarizer.
Supports fetching by fixed category or by free-text keyword,
with inline help tooltips for search refinement tips.
"""

from flask import Flask, render_template_string, request

from config import Config
from summarizer import NewsSummarizer

app = Flask(__name__)

CATEGORIES = ["business", "entertainment", "general", "health", "science", "sports", "technology"]

PAGE = """
<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>News Summarizer</title>
<style>
  :root {
    --bg: #f7f7fb;
    --card: #ffffff;
    --text: #1f2430;
    --muted: #6b7280;
    --accent: #4f46e5;
    --accent-soft: #eef2ff;
    --border: #e5e7eb;
    --positive: #16a34a;
    --negative: #dc2626;
    --neutral: #6b7280;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    padding: 40px 20px;
  }
  .wrap { max-width: 760px; margin: 0 auto; }
  h1 {
    font-size: 1.6rem;
    margin-bottom: 4px;
  }
  .subtitle {
    color: var(--muted);
    margin-top: 0;
    margin-bottom: 24px;
    font-size: 0.95rem;
  }
  form {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    display: grid;
    gap: 16px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
  }
  .field { display: flex; flex-direction: column; gap: 6px; }
  .field-label {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.9rem;
    font-weight: 600;
  }
  select, input[type=text], input[type=number] {
    padding: 9px 10px;
    border: 1px solid var(--border);
    border-radius: 8px;
    font-size: 0.95rem;
    background: #fff;
  }
  select:focus, input:focus {
    outline: none;
    border-color: var(--accent);
  }
  .help {
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: var(--accent-soft);
    color: var(--accent);
    font-size: 0.72rem;
    font-weight: 700;
    cursor: help;
  }
  .help .tooltip {
    visibility: hidden;
    opacity: 0;
    transition: opacity 0.15s ease;
    position: absolute;
    bottom: 140%;
    left: 50%;
    transform: translateX(-50%);
    background: #1f2430;
    color: #fff;
    padding: 10px 12px;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 400;
    line-height: 1.4;
    width: 260px;
    z-index: 10;
  }
  .help .tooltip::after {
    content: "";
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    border: 6px solid transparent;
    border-top-color: #1f2430;
  }
  .help:hover .tooltip, .help:focus .tooltip {
    visibility: visible;
    opacity: 1;
  }
  button {
    justify-self: start;
    background: var(--accent);
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
  }
  button:hover { background: #4338ca; }
  .results { margin-top: 28px; display: grid; gap: 14px; }
  .card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px 20px;
  }
  .card h3 { margin: 0 0 8px 0; font-size: 1.02rem; }
  .card .source { color: var(--muted); font-weight: 400; font-size: 0.85rem; }
  .card p { margin: 6px 0; font-size: 0.9rem; line-height: 1.45; }
  .badge {
    display: inline-block;
    padding: 2px 9px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    color: white;
  }
  .badge.positive { background: var(--positive); }
  .badge.negative { background: var(--negative); }
  .badge.neutral { background: var(--neutral); }
  a { color: var(--accent); text-decoration: none; font-size: 0.88rem; }
  a:hover { text-decoration: underline; }
  .cost {
    margin-top: 18px;
    padding: 10px 14px;
    background: var(--accent-soft);
    border-radius: 8px;
    font-size: 0.85rem;
    color: var(--accent);
    font-weight: 600;
  }
  .empty {
    margin-top: 20px;
    color: var(--muted);
    font-size: 0.9rem;
  }
</style>
</head>
<body>
<div class="wrap">
  <h1>News Summarizer</h1>
  <p class="subtitle">Fetch, summarize, and analyze the sentiment of news articles of the last seven days.</p>

  <form method="get">
    <div class="field">
      <span class="field-label">
        Category
        <span class="help" tabindex="0">i
          <span class="tooltip">Use a fixed news category (technology, health, etc.). Leave on "none" if you'd rather search by keyword below.</span>
        </span>
      </span>
      <select name="category">
        <option value="">-- none, use keyword --</option>
        {% for c in categories %}
          <option value="{{ c }}" {% if c == category %}selected{% endif %}>{{ c }}</option>
        {% endfor %}
      </select>
    </div>

    <div class="field">
      <span class="field-label">
        Keyword
        <span class="help" tabindex="0">i
          <span class="tooltip">Free-text search across all recent articles. Broad terms (e.g. "France") can return unrelated matches — try a more specific phrase like "France politics" or "France news", or wrap it in quotes (e.g. "France") for an exact match.</span>
        </span>
      </span>
      <input type="text" name="keyword" value="{{ keyword }}" placeholder='e.g. "artificial intelligence"'>
    </div>

    <div class="field">
      <span class="field-label">
        Number of articles
        <span class="help" tabindex="0">i
          <span class="tooltip">How many articles to fetch and process (1–10). More articles means more API calls and higher cost.</span>
        </span>
      </span>
      <input type="number" name="num" value="{{ num }}" min="1" max="10">
    </div>

    <button type="submit">Fetch &amp; Summarize</button>
  </form>

  {% if results %}
    <div class="results">
      {% for r in results %}
        <div class="card">
          <h3>{{ r.title }} <span class="source">— {{ r.source }}</span></h3>
          <p><b>Summary:</b> {{ r.summary }}</p>
          <p>
            <b>Sentiment:</b>
            {% if 'positive' in r.sentiment.lower() %}
              <span class="badge positive">Positive</span>
            {% elif 'negative' in r.sentiment.lower() %}
              <span class="badge negative">Negative</span>
            {% else %}
              <span class="badge neutral">Neutral</span>
            {% endif %}
            <br>{{ r.sentiment }}
          </p>
          <a href="{{ r.url }}" target="_blank">Read more →</a>
        </div>
      {% endfor %}
    </div>
    <div class="cost">{{ cost_summary }}</div>
  {% elif searched %}
    <p class="empty">No articles found. Try a different category or keyword.</p>
  {% endif %}
</div>
</body>
</html>
"""


@app.route("/")
def index():
    category = request.args.get("category", "")
    keyword = request.args.get("keyword", "")
    num = int(request.args.get("num", 3))

    results = None
    cost_summary = None
    searched = bool(request.args)

    if searched:
        config = Config()
        summarizer = NewsSummarizer(config)

        if keyword:
            results = summarizer.process_by_keyword(keyword, num_articles=num)
        elif category:
            results = summarizer.process_articles(category=category, num_articles=num)

        if results is not None:
            cost_summary = summarizer.cost_tracker.summary()

    return render_template_string(
        PAGE, categories=CATEGORIES, category=category, keyword=keyword, num=num,
        results=results, cost_summary=cost_summary, searched=searched,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)