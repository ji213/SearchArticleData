Overview:
    The project operates in two distinct phases:

    Ingestion Phase: import_articles.py fetches historical news data, handles environment variables via .env,   and uses SQL MERGE logic to ensure a deduplicated dataset.

    Summarization Phase: generate_article_summary.py identifies articles missing summaries, scrapes the full    text using Playwright (headless Chromium), and applies a frequency-based summarization algorithm.

Prerequisites
    Python 3.13+

    A running SQL Server instance with the dbo.tbl_articles table.

    A Perigon API Key.

    Playwright Browsers (Run playwright install chromium after setup).


Run Pipeline from Terminal:
    python import_articles.py

