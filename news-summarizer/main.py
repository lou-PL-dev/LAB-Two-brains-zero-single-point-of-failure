"""
main.py
Interactive application: lets the user choose a news category,
fetches articles, summarizes them, analyzes sentiment, and
shows a cost report.
"""

from config import Config
from summarizer import NewsSummarizer


VALID_CATEGORIES = [
    "business", "entertainment", "general",
    "health", "science", "sports", "technology",
]


def prompt_category():
    """Asks the user to pick a news category, with a sensible default."""
    print(f"Available categories: {', '.join(VALID_CATEGORIES)}")
    choice = input("Choose a category (press Enter for 'technology'): ").strip().lower()

    if not choice:
        return "technology"
    if choice not in VALID_CATEGORIES:
        print(f"'{choice}' not recognized, defaulting to 'technology'.")
        return "technology"
    return choice


def prompt_num_articles():
    """Asks the user how many articles to process, with validation."""
    choice = input("How many articles to process? (press Enter for 3): ").strip()

    if not choice:
        return 3
    try:
        num = int(choice)
        if num < 1:
            print("Must be at least 1, defaulting to 3.")
            return 3
        return num
    except ValueError:
        print("Not a valid number, defaulting to 3.")
        return 3


def main():
    print("=" * 60)
    print("NEWS SUMMARIZER — Interactive Mode")
    print("=" * 60)

    config = Config()
    missing = config.validate()
    if missing:
        print(f"Missing required configuration: {', '.join(missing)}")
        print("Please check your .env file before running this app.")
        return

    category = prompt_category()
    num_articles = prompt_num_articles()

    print(f"\nFetching and processing {num_articles} '{category}' articles...\n")

    summarizer = NewsSummarizer(config)
    results = summarizer.process_articles(category=category, num_articles=num_articles)

    if not results:
        print("No articles were found for this category. Try another one.")
        return
    
    if len(results) < num_articles:
        print(f"Note: only {len(results)} articles were available (requested {num_articles}).")

    summarizer.print_report(results)


if __name__ == "__main__":
    main()