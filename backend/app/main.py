# backend/app/main.py

import sys
import logging
from pathlib import Path

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import DATA_DIR, GROQ_API_KEY
from app.rag.loader import load_documents
from app.rag.chunker import chunk_documents
from app.rag.embeddings import embed_chunks
from app.rag.vector_store import get_collection, add_vectors, reset_collection
from app.rag.retriever import retrieve, format_results_for_prompt
from app.rag.generator import generate_answer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def index_documents():
    """
    Load, chunk, embed, and store documents in ChromaDB.
    """
    print("\n" + "=" * 60)
    print("📚 STEP 1: Loading Documents")
    print("=" * 60)
    
    if not DATA_DIR.exists():
        print(f"❌ Error: Data folder not found at {DATA_DIR}")
        print("   Please create the folder and add your documents.")
        return False
    
    # 1. Load
    documents, load_errors = load_documents(DATA_DIR)
    
    if not documents:
        print("❌ No documents loaded. Please add .txt, .pdf, or .docx files.")
        return False
    
    print(f"\n📄 Loaded {len(documents)} documents.")
    if load_errors:
        print(f"   ⚠️ {len(load_errors)} errors during loading.")
    
    # 2. Chunk
    print("\n" + "=" * 60)
    print("✂️ STEP 2: Chunking Documents")
    print("=" * 60)
    
    chunks, chunk_errors = chunk_documents(documents)
    
    if not chunks:
        print("❌ No chunks created. Check your documents for extractable text.")
        return False
    
    print(f"✅ Created {len(chunks)} total chunks.")
    if chunk_errors:
        print(f"   ⚠️ {len(chunk_errors)} errors during chunking.")
    
    # 3. Embed
    print("\n" + "=" * 60)
    print("🧠 STEP 3: Generating Embeddings")
    print("=" * 60)
    
    embedded, embed_errors = embed_chunks(chunks)
    
    if not embedded:
        print("❌ No chunks embedded. Check your embedding model.")
        return False
    
    print(f"✅ Embedded {len(embedded)} chunks.")
    if embed_errors:
        print(f"   ⚠️ {len(embed_errors)} errors during embedding.")
    
    # 4. Store
    print("\n" + "=" * 60)
    print("💾 STEP 4: Storing Vectors in ChromaDB")
    print("=" * 60)
    
    # Reset the collection to avoid duplicates (clean slate on each run)
    reset_collection()
    
    count, store_errors = add_vectors(embedded)
    
    if count == 0:
        print("❌ No vectors stored. Check your vector database.")
        return False
    
    print(f"✅ Stored {count} vectors in ChromaDB.")
    if store_errors:
        print(f"   ⚠️ {len(store_errors)} errors during storage.")
    
    # 5. Summary
    print("\n" + "=" * 60)
    print("🎉 INDEXING COMPLETE!")
    print("=" * 60)
    print(f"   📄 Documents: {len(documents)}")
    print(f"   ✂️ Chunks: {len(chunks)}")
    print(f"   🧠 Vectors: {len(embedded)}")
    print(f"   ❌ Total errors: {len(load_errors) + len(chunk_errors) + len(embed_errors) + len(store_errors)}")
    print("=" * 60)
    
    return True


def is_indexed() -> bool:
    """
    Check if the collection already has vectors (skips re-indexing).
    """
    try:
        collection = get_collection()
        count = collection.count()
        return count > 0
    except Exception:
        return False


def chat_loop():
    """
    Interactive chat loop where the user asks questions.
    """
    print("\n" + "=" * 60)
    print("💬 INTERACTIVE RAG CHAT")
    print("=" * 60)
    print("Type your questions about your documents.")
    print("Type 'exit' or 'quit' to stop.")
    print("Type 'sources' to show sources with the answer.")
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
            
            # Retrieve
            print("\n🔄 Searching...")
            results, ret_errors = retrieve(query)
            
            # Generate
            print("🤖 Generating answer...")
            answer, context = generate_answer(query, results)
            
            # Display answer
            print("\n" + "=" * 60)
            print("🤖 Answer:")
            print("=" * 60)
            print(answer)
            
            # Display sources
            if show_sources and results:
                print("\n" + "=" * 60)
                print("📚 Sources:")
                print("=" * 60)
                for i, r in enumerate(results, 1):
                    source = r['metadata'].get('source_file', 'unknown')
                    distance = r['distance']
                    text = r['text'][:200] + "..." if len(r['text']) > 200 else r['text']
                    print(f"\n[{i}] 📄 {source} (Relevance: {1 - distance:.2%})")
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


def main():
    """
    Main entry point for the RAG pipeline.
    """
    print("\n" + "=" * 60)
    print("🔒 SECURE MULTI-TENANT RAG")
    print("=" * 60)
    
    # Check for Groq API key
    if not GROQ_API_KEY or GROQ_API_KEY == "gsk_your-actual-api-key-here":
        print("\n⚠️ WARNING: GROQ_API_KEY not set in .env file.")
        print("   Please add your Groq API key to backend/.env")
        print("   Get one at: https://console.groq.com/keys")
        print("\n   Without it, the LLM will not work.")
        
        proceed = input("\nContinue anyway? (y/n): ").strip().lower()
        if proceed != "y":
            return
    
    # Check if documents are already indexed
    already_indexed = is_indexed()
    
    if already_indexed:
        print("\n✅ Documents are already indexed. Skipping re-indexing.")
        print("   To re-index, delete the 'chroma_db' folder and restart.")
        response = input("\nUse existing index? (Y/n): ").strip().lower()
        if response == "n":
            print("\n🗑️ Re-indexing documents...")
            success = index_documents()
            if not success:
                print("❌ Indexing failed. Exiting.")
                return
    else:
        print("\n🔨 First run: Indexing documents...")
        success = index_documents()
        if not success:
            print("❌ Indexing failed. Exiting.")
            return
    
    # Start chat
    chat_loop()


if __name__ == "__main__":
    main()