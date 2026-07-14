# backend/tests/test_loader.py
import pytest
from pathlib import Path
import sys

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.loader import load_documents


# ============================================================================
# EDGE CASE TESTS (Using tmp_path - No external files needed)
# These tests validate the logic using temporary files created during the test.
# ============================================================================

def test_load_empty_folder(tmp_path):
    """Test that an empty folder returns empty results."""
    documents, errors = load_documents(tmp_path)
    assert documents == {}
    assert errors == []


def test_skip_unsupported_files(tmp_path):
    """Test that unsupported file types are skipped and reported."""
    (tmp_path / "image.png").write_bytes(b"fake image")
    (tmp_path / "data.json").write_text('{"key": "value"}')
    
    documents, errors = load_documents(tmp_path)
    
    assert documents == {}
    assert len(errors) == 2
    assert all(e["type"] == "unsupported" for e in errors)
    # Check that both files appear in the errors (order doesn't matter)
    filenames = {e["file"] for e in errors}
    assert filenames == {"image.png", "data.json"}


def test_handle_empty_text_file(tmp_path):
    """Test that an empty text file is reported as an 'empty' error."""
    (tmp_path / "empty.txt").write_text("")  # Empty file
    
    documents, errors = load_documents(tmp_path)
    
    assert documents == {}
    assert len(errors) == 1
    assert errors[0]["file"] == "empty.txt"
    assert errors[0]["type"] == "empty"


def test_load_valid_text_file(tmp_path):
    """Test that a valid text file is loaded successfully."""
    (tmp_path / "hello.txt").write_text("Hello World!", encoding="utf-8")
    
    documents, errors = load_documents(tmp_path)
    
    assert "hello.txt" in documents
    assert documents["hello.txt"] == "Hello World!"
    assert errors == []


def test_mixed_files(tmp_path):
    """Test a mix of valid, empty, and unsupported files."""
    (tmp_path / "valid.txt").write_text("This is valid text.")
    (tmp_path / "empty.txt").write_text("")
    (tmp_path / "bad.exe").write_bytes(b"fake binary")
    
    documents, errors = load_documents(tmp_path)
    
    # Only the valid text file should be loaded
    assert "valid.txt" in documents
    assert len(documents) == 1
    
    # We should have 2 errors: one empty, one unsupported
    assert len(errors) == 2
    error_files = {e["file"] for e in errors}
    error_types = {e["type"] for e in errors}
    assert "empty.txt" in error_files
    assert "bad.exe" in error_files
    assert "empty" in error_types
    assert "unsupported" in error_types


# ============================================================================
# INTEGRATION TEST (Uses your actual `data/documents` folder)
# This test does NOT care about specific filenames. It just verifies the
# overall structure and behavior of the loader on your real files.
# ============================================================================

def test_loader_integration_general():
    """
    Runs the loader on the real data/documents folder.
    Completely general:
    - Does not assert specific filenames.
    - Only validates the structure of the return data.
    - Ensures the pipeline doesn't crash on your real documents.
    """
    data_folder = Path(__file__).parent.parent / "app" / "data" / "documents"
    
    # If the folder doesn't exist (e.g., in a fresh CI environment), skip gracefully.
    if not data_folder.exists():
        pytest.skip(f"Folder not found: {data_folder}")

    documents, errors = load_documents(data_folder)

    # --- 1. Validate Return Types ---
    assert isinstance(documents, dict), "documents should be a dict"
    assert isinstance(errors, list), "errors should be a list"

    # --- 2. Validate Every Loaded Document ---
    for filename, text in documents.items():
        assert isinstance(filename, str)
        assert isinstance(text, str)
        assert len(text) > 0, f"Loaded document {filename} has empty text (should have been an error)"

    # --- 3. Validate Every Error Structure ---
    for err in errors:
        assert "file" in err
        assert "error" in err
        assert "type" in err
        # Error types must be one of the expected values
        assert err["type"] in ["unsupported", "extraction", "dependency", "empty", "unknown"]

    # --- 4. Print a friendly summary so you can see what happened ---
    print(f"\n📊 Integration Test Summary:")
    print(f"   ✅ Loaded: {len(documents)} document(s)")
    if documents:
        print(f"      Files: {', '.join(documents.keys())}")
    print(f"   ❌ Errors: {len(errors)} issue(s)")
    if errors:
        for e in errors:
            print(f"      - {e['file']}: {e['error']} (Type: {e['type']})")

    # --- 5. Optional Sanity Check (Not required but safe) ---
    # If there are zero documents and zero errors, something is wrong (folder might be empty).
    # This ensures the test is actually testing something.
    assert not (len(documents) == 0 and len(errors) == 0), "Folder appears empty or no files were processed."