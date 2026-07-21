# backend/scripts/interactive_chat.py

import sys
from pathlib import Path

# Add the parent directory (backend/) to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging

from app.config import DATA_DIR, GROQ_API_KEY, GDRIVE_ROOT_FOLDER_ID
from app.rag.loader import load_documents
from app.rag.chunker import chunk_documents
from app.rag.embeddings import embed_chunks
from app.rag.vector_store import get_collection, add_vectors, reset_collection
from app.rag.retriever import retrieve, format_results_for_prompt
from app.rag.generator import generate_answer
from app.rag.gdrive_loader import stream_documents_from_gdrive
from app.rag.bm25_index import build_bm25_indexes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# =======================================================
# HELPER: Select Department & Role (Interactive)
# =======================================================
def select_multi_tenant_context():
    """Prompt the user to select their department and role."""
    print("\n" + "=" * 60)
    print("🔒 MULTI-TENANT CONTEXT SELECTOR")
    print("=" * 60)

    departments = ["Department_A", "Department_B"]
    roles_map = {
        "Department_A": ["Engineering", "Product", "Design"],
        "Department_B": ["Marketing", "Finance", "Sales"],
    }

    print("\n📁 Select your Department:")
    for i, dept in enumerate(departments, 1):
        print(f"   {i}. {dept}")
    print("   q. Quit")

    while True:
        choice = input("\nEnter number (1-2): ").strip()
        if choice.lower() == 'q':
            sys.exit(0)
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(departments):
                selected_dept = departments[idx]
                break
            else:
                print("Invalid choice. Please enter 1 or 2.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    print(f"\n🎯 Select your Role in {selected_dept}:")
    available_roles = roles_map[selected_dept]
    for i, role in enumerate(available_roles, 1):
        print(f"   {i}. {role}")

    while True:
        choice = input("\nEnter number: ").strip()
        if choice.lower() == 'q':
            sys.exit(0)
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(available_roles):
                selected_role = available_roles[idx]
                break
            else:
                print(f"Invalid choice. Please enter 1-{len(available_roles)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    print("\n" + "=" * 60)
    print(f"✅ Context set: {selected_dept} / {selected_role}")
    print("=" * 60)

    return selected_dept, selected_role


# =======================================================
# HELPER: Check if collection has documents
# =======================================================
def is_indexed() -> bool:
    """Check if the collection already has vectors."""
    try:
        collection = get_collection()
        count = collection.count()
        return count > 0
    except Exception:
        return False


# =======================================================
# INGESTION: From Google Drive (Multi-Tenant)
# =======================================================
def index_from_gdrive():
    """Load, chunk, embed, and store documents from Google Drive."""
    print("\n" + "=" * 60)
    print("📚 Indexing Documents from Google Drive")
    print("=" * 60)

    if not GDRIVE_ROOT_FOLDER_ID:
        print("❌ GDRIVE_ROOT_FOLDER_ID not set in .env")
        return False

    reset_collection()

    total_docs = 0
    total_chunks = 0
    total_embedded = 0

    for doc in stream_documents_from_gdrive(GDRIVE_ROOT_FOLDER_ID):
        total_docs += 1
        print(f"\n📄 Processing: {doc['file_name']}")
        print(f"   🏷️ Department: {doc['department']}, Role: {doc['role']}")

        chunks, chunk_errors = chunk_documents({doc["file_name"]: doc["text"]})
        if not chunks:
            print(f"   ⚠️ No chunks created for {doc['file_name']}")
            continue

        embedded, embed_errors = embed_chunks(chunks)
        if not embedded:
            print(f"   ⚠️ No embeddings for {doc['file_name']}")
            continue

        count, store_errors = add_vectors(
            embedded,
            metadata={
                "department": doc["department"],
                "role": doc["role"]
            }
        )

        total_chunks += len(chunks)
        total_embedded += count
        print(f"   ✅ Stored {count} chunks for {doc['file_name']}")

    print("\n" + "=" * 60)
    print("🎉 INDEXING COMPLETE!")
    print("=" * 60)
    print(f"   📄 Documents: {total_docs}")
    print(f"   ✂️ Chunks: {total_chunks}")
    print(f"   🧠 Vectors: {total_embedded}")
    print("=" * 60)

    return True


# =======================================================
# MAIN PIPELINE (CLI)
# =======================================================
def main():
    print("\n" + "=" * 60)
    print("🔒 SECURE MULTI-TENANT RAG (CLI)")
    print("=" * 60)

    if not GROQ_API_KEY or GROQ_API_KEY == "gsk_your-actual-api-key-here":
        print("\n⚠️ WARNING: GROQ_API_KEY not set in .env file.")
        print("   Please add your Groq API key to backend/.env")
        print("   Get one at: https://console.groq.com/keys")
        proceed = input("\nContinue anyway? (y/n): ").strip().lower()
        if proceed != "y":
            return

    department, role = select_multi_tenant_context()

    if not is_indexed():
        print("\n🔨 First run: Indexing documents from Google Drive...")
        if not index_from_gdrive():
            print("❌ Indexing failed. Exiting.")
            return
    else:
        print("\n✅ Documents are already indexed. Skipping re-indexing.")
        print("   To re-index, delete the 'chroma_db' folder and restart.")

    # Build BM25 indexes
    print("\n🔄 Building BM25 indexes for hybrid search...")
    build_bm25_indexes()
    print("✅ BM25 indexes ready.")

    print("\n" + "=" * 60)
    print("💬 INTERACTIVE RAG CHAT")
    print("=" * 60)
    print(f"🔒 Context: {department} / {role}")
    print("   Type 'exit' or 'quit' to stop.")
    print("   Type 'sources' to toggle source display.")
    print("=" * 60)

    show_sources = True

    while True:
        try:
            query = input("\n🤔 You: ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit", "bye"]:
                print("👋 Goodbye!")
                break
            if query.lower() == "sources":
                show_sources = not show_sources
                print(f"✅ Sources display: {'ON' if show_sources else 'OFF'}")
                continue

            print("\n🔄 Searching...")
            results, ret_errors = retrieve(query=query, department=department, role=role)

            print("🤖 Generating answer...")
            answer, context = generate_answer(query, results)

            print("\n" + "=" * 60)
            print("🤖 Answer:")
            print("=" * 60)
            print(answer)

            if show_sources and results:
                print("\n" + "=" * 60)
                print("📚 Sources:")
                print("=" * 60)
                for i, r in enumerate(results, 1):
                    source = r['metadata'].get('source_file', 'unknown')
                    dept = r['metadata'].get('department', 'unknown')
                    role_src = r['metadata'].get('role', 'unknown')
                    distance = r['distance']
                    text = r['text'][:200] + "..." if len(r['text']) > 200 else r['text']
                    print(f"\n[{i}] 📄 {source} ({dept}/{role_src})")
                    print(f"    Relevance: {1 - distance:.2%}")
                    print(f"    {text}")

            if ret_errors:
                print("\n⚠️ Retrieval errors:")
                for e in ret_errors:
                    print(f"   - {e['error']}")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logger.error(f"Chat loop error: {e}")


if __name__ == "__main__":
    main()