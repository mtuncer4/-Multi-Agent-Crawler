# Product Requirements Document (PRD)
**Project:** HW2 - Build Google with Multi-Agent AI  
**Focus:** AI Agent Workflow & Web Crawling/Search system  

## 1. Executive Summary
This project aims to build a conceptual web crawler and search utility representing the foundational pillars of a search engine. It is built strictly using language-native features (Python standard library) without robust standalone indexing engines (e.g., Elasticsearch) or crawler frameworks (e.g., Scrapy). The development process serves as a demonstration of a multi-agent AI workflow.

## 2. Core Requirements

### 2.1 Indexing (Web Crawler)
*   **Method Signature:** `index(origin, k)`
*   **Behavior:** Initiates web crawl from `origin` URL to a maximum depth of `k`. (Depth is the number of hops from the origin).
*   **Constraints:**
    *   Never crawl the same page twice.
    *   System must include a back-pressure mechanism (e.g., queue size limit or throughput restriction) to handle large theoretical scale gracefully without exhausting system memory.
    *   Must only use native features.

### 2.2 Searching
*   **Method Signature:** `search(query)`
*   **Behavior:** Accepts a string query and returns relevant URLs.
*   **Output Format:** Returns a list of triples in the format: `(relevant_url, origin_url, depth)`.
*   **Concurrency:** Search operations must be executable while the indexing engine is still active in the background, instantly reflecting newly discovered results.
*   **Relevancy:** Search will use a simple, assumption-based relevancy model (e.g., keyword count or existence check) due to native-language constraints.

### 2.3 User Interface (CLI)
*   Provides an interactive way to initiate `index` and `search` operations.
*   Must display system state:
    *   Indexing progress (pages crawled vs pending).
    *   Queue depth / Back-pressure status.
*   **Bonus Feature:** Resume after an interruption. The system should pick up from its previous state instead of starting from scratch.

## 3. Assumptions
*   Text parsing will rely on simple HTML tag stripping to find `<a href="...">` and text content.
*   The "scale" mentioned focuses on safe queueing sizes and thread throttling rather than multi-node distributed network crawling.
*   SQLite is sufficient to satisfy the local execution, concurrency, and resumability requirements cleanly.

## 4. Acceptance Criteria
*   The system successfully builds an index within the specified depth `k`.
*   Data persists across restarts (resumability).
*   Console UI gives live feedback.
*   Search returns the expected tuple structure accurately indicating the lineage of the discovery.
