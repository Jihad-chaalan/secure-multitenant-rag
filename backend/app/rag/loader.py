import logging
from pathlib import Path
from typing import Dict, Callable, List, Tuple

# --- (Graceful fallback) ---
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from docx import Document
except ImportError:
    Document = None


# --- 2. SETUP LOGGING ---
logger = logging.getLogger(__name__)


# --- 3. INDIVIDUAL HANDLER FUNCTIONS (Each does one thing well) ---
#i do it like one thing function because if i want to handle new extension using open clased principle

def _handle_txt(file_path: Path) -> str:
    """Reads a text file with encoding fallback."""
    encodings = ["utf-8", "latin-1", "cp1252"]
    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding, errors="ignore") as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    # Ultimate fallback
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def _handle_pdf(file_path: Path) -> str:
    """Extracts text from a PDF file."""
    if PdfReader is None:
        raise ImportError("pypdf library is required for PDF files.")
    
    reader = PdfReader(file_path)
    text_parts = [page.extract_text() for page in reader.pages if page.extract_text()]
    return " ".join(text_parts)


def _handle_docx(file_path: Path) -> str:
    """Extracts text from a DOCX file."""
    if Document is None:
        raise ImportError("python-docx library is required for DOCX files.")
    
    doc = Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


# --- 4. THE REGISTRY (Maps extensions to their handlers) ---

_HANDLERS: Dict[str, Callable[[Path], str]] = {
    ".txt": _handle_txt,
    ".pdf": _handle_pdf,
    ".docx": _handle_docx,
}

SUPPORTED_EXTENSIONS = set(_HANDLERS.keys())


# --- 5. THE PUBLIC API (Returns both documents and errors) ---

def load_documents(folder_path: Path) -> Tuple[Dict[str, str], List[Dict[str, str]]]:
    """
    Read all supported documents from a folder.

    Supported formats: .txt, .pdf, .docx

    Args:
        folder_path: Path to the folder containing documents.

    Returns:
        A tuple of (documents, errors):
            - documents: Dict[str, str] mapping filename -> extracted text.
            - errors: List of Dict with keys: "file", "error", "type"
                      (type can be: "unsupported", "extraction", "dependency", "empty")

    Raises:
        FileNotFoundError: If the folder does not exist.
        NotADirectoryError: If the path is not a directory.
    """
    if not folder_path.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")
    if not folder_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {folder_path}")

    # Warn about missing optional libraries (once)
    if PdfReader is None and any(f.suffix == ".pdf" for f in folder_path.glob("*.*")):
        logger.warning("pypdf not installed. PDF files will fail.")
    if Document is None and any(f.suffix == ".docx" for f in folder_path.glob("*.*")):
        logger.warning("python-docx not installed. DOCX files will fail.")

    documents: Dict[str, str] = {}
    errors: List[Dict[str, str]] = []

    for file_path in folder_path.glob("*.*"):
        if not file_path.is_file():
            continue

        ext = file_path.suffix.lower()
        filename = file_path.name

        # 1. Skip unsupported extensions
        if ext not in SUPPORTED_EXTENSIONS:
            logger.info(f"Skipping unsupported file: {filename}")
            errors.append({
                "file": filename,
                "error": f"Unsupported extension: {ext}",
                "type": "unsupported"
            })
            continue

        # 2. Look up the handler in the registry
        handler = _HANDLERS[ext]
        logger.info(f"Processing: {filename}")

        try:
            raw_text = handler(file_path)
            if raw_text and raw_text.strip():
                documents[filename] = raw_text
                logger.info(f"   ✅ Loaded {len(raw_text)} characters.")
            else:
                errors.append({
                    "file": filename,
                    "error": "File contains no extractable text.",
                    "type": "empty"
                })
                logger.warning(f"   ⚠️ No text extracted from {filename}")

        except ImportError as e:
            errors.append({
                "file": filename,
                "error": str(e),
                "type": "dependency"
            })
            logger.error(f"   ❌ Missing dependency: {e}")

        except Exception as e:
            errors.append({
                "file": filename,
                "error": str(e),
                "type": "extraction"
            })
            logger.error(f"   ❌ Error reading {filename}: {e}")

    logger.info(f"✅ Loaded {len(documents)} documents. ❌ {len(errors)} errors.")
    return documents, errors


