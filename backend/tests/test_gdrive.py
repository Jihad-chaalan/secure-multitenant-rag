# backend/tests/test_gdrive.py
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.gdrive_loader import load_documents_from_gdrive
from app.config import GDRIVE_ROOT_FOLDER_ID

# Check if credentials file exists
CREDENTIALS_PATH = Path(__file__).parent.parent / "gdrive_credentials.json"



def test_stream_documents_from_gdrive():
    """
    Explicitly test the streaming generator directly.
    Validates that the generator yields the correct structure and data.
    """
    # --- 1. Skip conditions (for CI/CD) ---
    if not CREDENTIALS_PATH.exists():
        pytest.skip("gdrive_credentials.json not found. Skipping GDrive test.")
    
    if not GDRIVE_ROOT_FOLDER_ID:
        pytest.skip("GDRIVE_ROOT_FOLDER_ID not set in .env. Skipping GDrive test.")

    # --- 2. Import the generator directly ---
    from app.rag.gdrive_loader import stream_documents_from_gdrive

    # --- 3. Iterate through the generator ---
    doc_count = 0
    for doc in stream_documents_from_gdrive(GDRIVE_ROOT_FOLDER_ID):
        # a) Validate that the document has the required keys
        assert "file_name" in doc, "Missing 'file_name' in yielded document"
        assert "text" in doc, "Missing 'text' in yielded document"
        assert "department" in doc, "Missing 'department' in yielded document"
        assert "role" in doc, "Missing 'role' in yielded document"
        
        # b) Validate that the text is non-empty
        assert len(doc["text"]) > 0, f"Document {doc['file_name']} has empty text"
        
        # c) Validate department and role values
        assert doc["department"] in ["Department_A", "Department_B"], f"Unexpected department: {doc['department']}"
        assert doc["role"] in [
            "Engineering", "Product", "Design",  # Dept A roles
            "Marketing", "Finance", "Sales"      # Dept B roles
        ], f"Unexpected role: {doc['role']}"
        
        doc_count += 1

    # --- 4. Ensure it found at least 1 document (sanity check) ---
    assert doc_count > 0, "Streaming generator yielded 0 documents"
    
    # --- 5. Compare count with batch loader to ensure no data loss ---
    from app.rag.gdrive_loader import load_documents_from_gdrive
    batch_docs, _ = load_documents_from_gdrive(GDRIVE_ROOT_FOLDER_ID)
    assert doc_count == len(batch_docs), (
        f"Count mismatch: Generator yielded {doc_count}, Batch loader found {len(batch_docs)}"
    )

    print(f"\n📊 Streaming Generator Test Passed:")
    print(f"   ✅ Total documents yielded: {doc_count}")

def test_gdrive_loader_metadata():
    """
    Integration test for Google Drive loader with metadata extraction.
    
    Validates:
    1. Authentication and file downloading still work.
    2. The connector correctly extracts 'department' and 'role' from the folder path.
    3. The data is returned in the correct format.
    """
    # --- 1. Skip conditions (for CI/CD) ---
    if not CREDENTIALS_PATH.exists():
        pytest.skip("gdrive_credentials.json not found. Skipping GDrive test.")
    
    if not GDRIVE_ROOT_FOLDER_ID:
        pytest.skip("GDRIVE_ROOT_FOLDER_ID not set in .env. Skipping GDrive test.")

    # --- 2. Load documents from Google Drive ---
    documents, errors = load_documents_from_gdrive(GDRIVE_ROOT_FOLDER_ID)

    # --- 3. Validate that documents were loaded (sanity check) ---
    assert len(documents) > 0, "No documents loaded from Google Drive"
    assert len(errors) == 0, f"Errors encountered: {errors}"

    # --- 4. NEW: Validate METADATA extraction for every document ---
    for doc in documents:
        # a) Check that the document has the required keys
        assert "file_name" in doc, "Missing 'file_name' in document"
        assert "text" in doc, "Missing 'text' in document"
        assert "department" in doc, "Missing 'department' in document"
        assert "role" in doc, "Missing 'role' in document"
        
        # b) Check that the extracted text is non-empty
        assert len(doc["text"]) > 0, f"Document {doc['file_name']} has empty text"
        
        # c) Check that department and role are not 'Unknown'
        #    (This would indicate your folder structure is flat or misconfigured)
        assert doc["department"] != "Unknown", f"Department extraction failed for {doc['file_name']}"
        assert doc["role"] != "Unknown", f"Role extraction failed for {doc['file_name']}"
        
        # d) Validate the specific naming based on your new folder structure
        #    (These assertions are optional but highly recommended for your demo)
        assert doc["department"] in ["Department_A", "Department_B"], f"Unexpected department: {doc['department']}"
        assert doc["role"] in [
            "Engineering", "Product", "Design",  # Dept A roles
            "Marketing", "Finance", "Sales"      # Dept B roles
        ], f"Unexpected role: {doc['role']}"

    # --- 5. Print a summary for debugging (visible in pytest -v) ---
    print(f"\n📊 GDrive Multi-Tenancy Test Passed:")
    print(f"   ✅ Total documents: {len(documents)}")
    print(f"   📁 Departments found: {set(d['department'] for d in documents)}")
    print(f"   🧑‍💼 Roles found: {set(d['role'] for d in documents)}")
    print(f"   ❌ Total errors: {len(errors)}")