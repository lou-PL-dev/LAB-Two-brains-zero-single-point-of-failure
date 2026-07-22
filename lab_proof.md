# Lab Proof — News Summarizer

This file is the entry point for reviewing this lab. It links each checkpoint to its evidence.

## Setup
- ✅ `python config.py` → validated successfully (all required keys present)

## Checkpoints

| Checkpoint | Evidence |
|---|---|
| Config validation | Ran `python config.py` — see [Screenshots](./Sucessful_config.png) |
| News API fetch (3 articles) | Ran `python news_api.py` |
| LLM providers test (OpenAI + Cohere) | Ran `python llm_providers.py` — cost tracking confirmed |
| Summarizer core logic | Ran `python summarizer.py --sync` — full report generated |
| Async processing | Ran `python summarizer.py --async` — same output, concurrent execution |
| Unit tests | Ran `pytest test_summarizer.py -v` → **7/7 passed** — see [`Screenshots/pytest_results.png`](./Test_proof.png) |
| Main application | Ran `python main.py` → interactive mode, processed 4 "health" articles — see [`Screenshots/main_app_run.png`](./News summarized) |

## How to reproduce

```bash
cd news-summarizer
pip install -r requirements.txt
python config.py
python main.py
```

## Notes
- No API keys or secrets are committed — see `.env.example` for the required variables.