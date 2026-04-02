# langchain-indexing-experiment

A toy experiment demonstrating LangChain's `SQLRecordManager` + FAISS as a replacement for custom vector-store state-management boilerplate.

## Purpose

This project validates three ideas:

1. **Upstream deduplication** — The `SQLRecordManager` hashes document content at ingestion time. Re-indexing the same document is a no-op; mutating a document automatically deletes the stale vector and adds the new one. No custom audit scripts needed.

2. **Relational inventory** — Instead of scanning the entire FAISS index into RAM to list what files are indexed (an O(N) memory operation), we query the SQLite database maintained by the Record Manager directly. This is an O(1) memory operation regardless of corpus size.

3. **Persistence round-trip** — The FAISS index is saved to disk with `save_local`, then reloaded into a fresh Python object. Re-indexing the same documents against the reloaded store is still a no-op because the `SQLRecordManager` (backed by `vector_cache.db`) already holds their content hashes. The two stores stay in sync across process restarts.

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

=== Section C: Persistence Round-Trip ===

FAISS index saved to ./faiss_store/
FAISS index reloaded from disk.

Re-index after reload: {'num_added': 0, 'num_updated': 0, 'num_skipped': 2, 'num_deleted': 0}

=> skipped=2 confirms the record manager state survived the save/reload cycle.
```

## Structure

- `main.py` — single runnable script with all demos
- `vector_cache.db` — SQLite record manager database, created at runtime (gitignored)
- `faiss_store/` — persisted FAISS index, created at runtime (gitignored)
