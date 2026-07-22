"""
llm_providers.py
Wraps OpenAI and Cohere APIs with cost tracking and a simple retry mechanism.
"""

import time
from openai import OpenAI
import cohere
from config import Config


# Rough per-1K-token prices (USD) — adjust to current pricing if needed
PRICING = {
    "openai": {"input": 0.0005, "output": 0.0015},   # e.g. gpt-4o-mini range
    "cohere": {"input": 0.0000, "output": 0.0000},    # free trial key — no cost, tracked for structure/consistency
}


class CostTracker:
    """Tracks cumulative API spend across providers."""

    def __init__(self):
        self.total_cost = 0.0
        self.calls = []

    def add(self, provider, input_tokens, output_tokens):
        rates = PRICING[provider]
        cost = (input_tokens / 1000) * rates["input"] + (output_tokens / 1000) * rates["output"]
        self.total_cost += cost
        self.calls.append({"provider": provider, "cost": cost})
        return cost

    def summary(self):
        return f"Total spent: ${self.total_cost:.4f} across {len(self.calls)} calls"


class LLMProviders:
    """Wraps OpenAI and Cohere clients with basic retry logic."""

    def __init__(self, config: Config, cost_tracker: CostTracker):
        self.openai_client = OpenAI(api_key=config.openai_api_key)
        self.cohere_client = cohere.ClientV2(api_key=config.cohere_api_key)
        self.max_retries = config.max_retries
        self.cost_tracker = cost_tracker

    def summarize_with_openai(self, text, model="gpt-4o-mini"):
        """Summarizes text using OpenAI. Returns summary string."""
        for attempt in range(self.max_retries):
            try:
                response = self.openai_client.chat.completions.create(
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
                print(f"OpenAI attempt {attempt + 1} failed: {e}")
                time.sleep(1)
        return None

    def analyze_sentiment_with_cohere(self, text, model="command-r-plus-08-2024"):
        """Analyzes sentiment using Cohere. Returns sentiment label + reasoning."""
        for attempt in range(self.max_retries):
            try:
                response = self.cohere_client.chat(
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
                print(f"Cohere attempt {attempt + 1} failed: {e}")
                time.sleep(1)
        return None


if __name__ == "__main__":
    config = Config()
    tracker = CostTracker()
    providers = LLMProviders(config, tracker)

    sample_text = "Apple announced a major update to its AI features today, drawing praise from developers."

    print("Testing OpenAI summarization...")
    summary = providers.summarize_with_openai(sample_text)
    print(f"Summary: {summary}\n")

    print("Testing Cohere sentiment analysis...")
    sentiment = providers.analyze_sentiment_with_cohere(sample_text)
    print(f"Sentiment: {sentiment}\n")

    print(tracker.summary())