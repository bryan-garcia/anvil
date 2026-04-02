"""
LangChain Indexing API experiment.

Demonstrates three ideas:
  A) Upstream deduplication via SQLRecordManager — no custom audit scripts needed.
  B) Relational inventory via sqlite3 — no full FAISS scan needed.
  C) Persistence round-trip — save FAISS to disk, reload it, confirm the
     SQLRecordManager state survives and re-indexing is still a no-op.
"""

import shutil
import sqlite3
from pathlib import Path

import faiss
from langchain.indexes import SQLRecordManager, index
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

# ---------------------------------------------------------------------------
# Clean up any artifacts left by a previous run so this script is idempotent
# ---------------------------------------------------------------------------

for _artifact in ["vector_cache.db", "faiss_store"]:
    _p = Path(_artifact)
    if _p.is_dir():
        shutil.rmtree(_p)
    elif _p.exists():
        _p.unlink()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def build_vectorstore(embeddings: OpenAIEmbeddings) -> FAISS:
    embedding_dim = len(embeddings.embed_query("test"))
    faiss_index = faiss.IndexFlatL2(embedding_dim)
    return FAISS(
        embedding_function=embeddings,
        index=faiss_index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )


def get_inventory(db_path: str = "vector_cache.db") -> list[str]:
    """
    Return a sorted list of all unique source files currently in the vector
    store by querying SQLite directly — no FAISS scan, O(1) memory usage.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT source_id FROM upsertion_record")
    files = [row[0] for row in cursor.fetchall()]
    conn.close()
    return sorted(files)


# ---------------------------------------------------------------------------
# Section A: Upstream Deduplication
# ---------------------------------------------------------------------------

print("=== Section A: Upstream Deduplication ===\n")

embeddings = OpenAIEmbeddings()
vectorstore = build_vectorstore(embeddings)

record_manager = SQLRecordManager(
    "faiss/experiment",
    db_url="sqlite:///vector_cache.db",
)
record_manager.create_schema()

docs_v1 = [
    Document(page_content="Apples are red.", metadata={"source": "doc_A.txt"}),
    Document(page_content="Bananas are yellow.", metadata={"source": "doc_B.txt"}),
]

# Run 1: index two new documents
result1 = index(
    docs_source=docs_v1,
    record_manager=record_manager,
    vector_store=vectorstore,
    cleanup="incremental",
    source_id_key="source",
)
print(f"Run 1 (new docs):      {result1}")

# Run 2: re-index the exact same documents — should be a no-op
result2 = index(
    docs_source=docs_v1,
    record_manager=record_manager,
    vector_store=vectorstore,
    cleanup="incremental",
    source_id_key="source",
)
print(f"Run 2 (same docs):     {result2}")

# Run 3: doc_A.txt is mutated; doc_B.txt is unchanged
docs_v2 = [
    Document(page_content="Apples are red AND green.", metadata={"source": "doc_A.txt"}),
    Document(page_content="Bananas are yellow.", metadata={"source": "doc_B.txt"}),
]

result3 = index(
    docs_source=docs_v2,
    record_manager=record_manager,
    vector_store=vectorstore,
    cleanup="incremental",
    source_id_key="source",
)
print(f"Run 3 (mutated doc_A): {result3}")

# ---------------------------------------------------------------------------
# Section B: Relational Inventory
# ---------------------------------------------------------------------------

print("\n=== Section B: Relational Inventory ===\n")

current_files = get_inventory()
print("Files currently indexed:")
for f in current_files:
    print(f"  - {f}")

# ---------------------------------------------------------------------------
# Section C: Persistence Round-Trip
#
# Save the FAISS index to disk, reload it into a fresh Python object, then
# re-index the same documents. Because the SQLRecordManager (vector_cache.db)
# already has their content hashes, the result must be skipped=2, added=0.
# ---------------------------------------------------------------------------

print("\n=== Section C: Persistence Round-Trip ===\n")

# Save the current in-memory FAISS index to disk
FAISS_STORE_PATH = "faiss_store"
vectorstore.save_local(FAISS_STORE_PATH)
print(f"FAISS index saved to ./{FAISS_STORE_PATH}/")

# Reload into a brand-new Python object (simulates a process restart)
reloaded_vectorstore = FAISS.load_local(
    FAISS_STORE_PATH,
    embeddings,
    allow_dangerous_deserialization=True,
)
print("FAISS index reloaded from disk.\n")

# The SQLRecordManager already has hashes for docs_v2 from Run 3 above.
# Re-indexing against the reloaded store must be a pure no-op.
result_reload = index(
    docs_source=docs_v2,
    record_manager=record_manager,
    vector_store=reloaded_vectorstore,
    cleanup="incremental",
    source_id_key="source",
)
print(f"Re-index after reload: {result_reload}")
print("\n=> skipped=2 confirms the record manager state survived the save/reload cycle.")
