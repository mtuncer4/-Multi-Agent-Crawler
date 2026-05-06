# Multi-Agent Web Crawler

This conceptual project implements a single-node web crawler and search engine relying entirely on Python's native standard libraries. It uses a SQLite-backed task queue to enforce back-pressure limits and ensure system state resumability. We utilized a Multi-Agent AI development workflow to split system responsibilities.

## Requirements
*   Python 3.8+
*   No external libraries are required (e.g., no `requests`, `scrapy`, or `beautifulsoup4`).

## How to Run

1.  Open your terminal.
2.  Run the main application:
    ```bash
    python main.py
    ```
3.  The CLI will present an interactive prompt where you can:
    *   Initiate a crawl using the `index` command.
    *   Search indexed documents returning **ranked results** (scored by keyword frequency).
    *   Use the `resume` command to prove **resumability** constraints (pushes failed/interrupted jobs back into pending).
    *   View real-time crawler progress, job stats, and **queue depth visibility** through the `status` command.

## Core Structure
*   **Indexer/Crawler:** Runs asynchronously via `threading`. Honors maximum queue depth natively directly at insertion (**back-pressure limit**) and respects individual job depths.
*   **Search Engine:** Reads concurrently from the database returning true relevancy scores.
*   **Database:** `src/db.py` contains the table and query schema supporting atomic transactions and cross-thread cursor handling. It provides full persistence.

## AI Agent Details
See the `/agents/` directory for system prompts showcasing how responsibilities were distributed to build this software.
