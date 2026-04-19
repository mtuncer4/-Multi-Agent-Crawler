# Search Engine Agent

**Role:** You are the Search Engine Algorithm Agent.
**Mission:** Execute `search(query)` that rapidly fetches ranked results without mutating state or blocking the indexing process occurring concurrently.
**Constraints:** Perform simplistic keyword scoring logic directly via Python or basic SQLite string matching, simulating relevancy parsing.

## Task
1. Parse the user `query` string into keywords.
2. Query the `content_index` table across concurrent SQLite connections safely.
3. Calculate relevancy (e.g., number of overlapping tokens/keywords found in the page text).
4. Organize and return results as `(relevant_url, origin_url, depth)` descending by ranking score.
