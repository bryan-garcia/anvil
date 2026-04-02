# langchain-indexing-experiment

A toy experiment demonstrating LangChain's `SQLRecordManager` + FAISS as a replacement for custom vector-store state-management boilerplate.

## Purpose

This project validates two ideas:

1. **Upstream deduplication** — The `SQLRecordManager` hashes document content at ingestion time. Re-indexing the same document is a no-op; mutating a document automatically deletes the stale vector and adds the new one. No custom audit scripts needed.

2. **Relational inventory** — Instead of scanning the entire FAISS index into RAM to list what files are indexed (an O(N) memory operation), we query the SQLite database maintained by the Record Manager directly. This is an O(1) memory operation regardless of corpus size.

## Setup

```bash
uv venv
uv pip install -e .
```

Requires an OpenAI API key:

```bash
export OPENAI_API_KEY=sk-...
```

## Run

```bash
python main.py
```

Expected output:

```
=== Section A: Upstream Deduplication ===

Run 1 (new docs):      {'num_added': 2, 'num_updated': 0, 'num_skipped': 0, 'num_deleted': 0}
Run 2 (same docs):     {'num_added': 0, 'num_updated': 0, 'num_skipped': 2, 'num_deleted': 0}
Run 3 (mutated doc_A): {'num_added': 1, 'num_updated': 0, 'num_skipped': 1, 'num_deleted': 1}

=== Section B: Relational Inventory ===

Files currently indexed:
- doc_A.txt
- doc_B.txt
```

## Structure

- `main.py` — single runnable script with all demos
- `vector_cache.db` — SQLite database created at runtime (gitignored)
