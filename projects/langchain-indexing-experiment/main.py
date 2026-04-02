"""
LangChain Indexing API experiment.

Demonstrates two ideas:
  A) Upstream deduplication via SQLRecordManager — no custom audit scripts needed.
  B) Relational inventory via sqlite3 — no full FAISS scan needed.
"""

import sqlite3

import faiss
from langchain.indexes import SQLRecordManager, index
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings


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
