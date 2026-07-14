# backend/app/rag/chunker.py

import logging
from typing import Dict, List, Tuple
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)


def chunk_documents(
    documents: Dict[str, str]
) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """
    Split documents into overlapping chunks.

    Args:
        documents: Dictionary mapping filename -> raw text (from loader)

    Returns:
        A tuple of (chunks, errors):
            - chunks: List of Dict with keys: "text", "source_file", "chunk_index"
            - errors: List of Dict with keys: "file", "error", "type"
    """
    if not documents:
        logger.warning("No documents provided to chunker.")
        return [], []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    all_chunks: List[Dict[str, str]] = []
    errors: List[Dict[str, str]] = []

    for filename, text in documents.items():
        # Skip empty text
        if not text or not text.strip():
            errors.append({
                "file": filename,
                "error": "Document is empty or contains only whitespace.",
                "type": "empty"
            })
            logger.warning(f"⚠️ Skipping empty document: {filename}")
            continue

        try:
            # Split the text
            raw_chunks = text_splitter.split_text(text)

            if not raw_chunks:
                errors.append({
                    "file": filename,
                    "error": "Splitting resulted in zero chunks.",
                    "type": "empty"
                })
                logger.warning(f"⚠️ No chunks generated for: {filename}")
                continue

            # Add metadata to each chunk
            for idx, chunk_text in enumerate(raw_chunks):
                all_chunks.append({
                    "text": chunk_text,
                    "source_file": filename,
                    "chunk_index": idx
                })

            logger.info(f"   ✂️ {filename} -> {len(raw_chunks)} chunks")

        except Exception as e:
            errors.append({
                "file": filename,
                "error": f"Chunking failed: {str(e)}",
                "type": "extraction"
            })
            logger.error(f"   ❌ Chunking failed for {filename}: {e}")

    logger.info(f"✅ Total chunks created: {len(all_chunks)}. Errors: {len(errors)}")
    return all_chunks, errors