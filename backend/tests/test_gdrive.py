# backend/tests/test_gdrive.py
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.gdrive_loader import load_documents_from_gdrive
from app.config import GDRIVE_FOLDER_ID


# Check if credentials file exists
CREDENTIALS_PATH = Path(__file__).parent.parent / "gdrive_credentials.json"


def test_gdrive_loader():
    """Integration test for Google Drive loader.
    
    This test is skipped if:
    - gdrive_credentials.json is not found (CI/CD)
    - GDRIVE_FOLDER_ID is not set in .env
    """
    # 1. Check for credentials file
    if not CREDENTIALS_PATH.exists():
        pytest.skip("gdrive_credentials.json not found. Skipping GDrive test.")
    
    # 2. Check for folder ID
    if not GDRIVE_FOLDER_ID:
        pytest.skip("GDRIVE_FOLDER_ID not set in .env. Skipping GDrive test.")
    
    # 3. Run the loader
    documents, errors = load_documents_from_gdrive(GDRIVE_FOLDER_ID)
    
    # 4. Assertions
    assert len(documents) > 0, "No documents loaded from Google Drive"
    assert len(errors) == 0, f"Errors encountered: {errors}"
    
    # 5. Validate each document
    for filename, text in documents.items():
        assert len(text) > 0, f"Document {filename} has empty text"
        
    
    print(f"\n📊 GDrive Integration Test Passed:")
    print(f"   ✅ Loaded {len(documents)} documents.")