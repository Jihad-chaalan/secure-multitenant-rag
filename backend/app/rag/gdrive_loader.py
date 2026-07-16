# backend/app/rag/gdrive_loader.py

import tempfile
import logging
from pathlib import Path
from typing import Dict, List, Tuple

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from app.rag.loader import _handle_pdf, _handle_docx, _handle_txt

logger = logging.getLogger(__name__)

# Path to your service account JSON file (relative to project root)
SERVICE_ACCOUNT_FILE = Path(__file__).parent.parent.parent / "gdrive_credentials.json"
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


def get_drive_service():
    """Authenticate and return the Google Drive service."""
    if not SERVICE_ACCOUNT_FILE.exists():
        raise FileNotFoundError(
            f"Service account file not found: {SERVICE_ACCOUNT_FILE}. "
            "Please download the JSON key and place it in the backend folder."
        )
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build('drive', 'v3', credentials=creds)


def list_files_in_folder(service, folder_id: str) -> List[Dict]:
    """List all files (not folders) inside a given Google Drive folder."""
    results = []
    page_token = None
    while True:
        response = service.files().list(
            q=f"'{folder_id}' in parents and mimeType!='application/vnd.google-apps.folder'",
            spaces='drive',
            fields='nextPageToken, files(id, name, mimeType)',
            pageToken=page_token
        ).execute()
        results.extend(response.get('files', []))
        page_token = response.get('nextPageToken')
        if not page_token:
            break
    return results


def download_and_extract_file(service, file_id: str, file_name: str) -> Tuple[str, str]:
    """
    Downloads a file from GDrive to a temporary file, extracts text,
    and cleans up the temp file. Returns (extracted_text, error_message).
    """
    ext = Path(file_name).suffix.lower()
    if ext not in [".txt", ".pdf", ".docx"]:
        return "", f"Unsupported file type: {ext}"

    # Create a temporary file on disk (prevents OOM)
    temp_file = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
    temp_path = Path(temp_file.name)

    try:
        # Download the file in chunks
        request = service.files().get_media(fileId=file_id)
        downloader = MediaIoBaseDownload(temp_file, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()

        temp_file.close()

        # Use your existing handlers (they accept file paths)
        if ext == ".pdf":
            text = _handle_pdf(temp_path)
        elif ext == ".docx":
            text = _handle_docx(temp_path)
        elif ext == ".txt":
            text = _handle_txt(temp_path)
        else:
            return "", "Unsupported extension"

        if not text or not text.strip():
            return "", "No text extracted"

        return text, ""

    except Exception as e:
        logger.error(f"Error processing {file_name}: {e}")
        return "", str(e)

    finally:
        # Always delete the temporary file
        if temp_path.exists():
            temp_path.unlink()


def load_documents_from_gdrive(folder_id: str) -> Tuple[Dict[str, str], List[Dict]]:
    """
    Main function: Load all supported documents from a specific Google Drive folder.
    Returns (documents_dict, errors_list) – same format as load_documents().
    """
    service = get_drive_service()
    files = list_files_in_folder(service, folder_id)

    if not files:
        logger.warning(f"No files found in folder ID: {folder_id}")
        return {}, []

    documents = {}
    errors = []

    logger.info(f"📁 Found {len(files)} files in GDrive folder.")

    for file in files:
        logger.info(f"📄 Processing: {file['name']}")
        text, error = download_and_extract_file(service, file['id'], file['name'])

        if error:
            errors.append({
                "file": file['name'],
                "error": error,
                "type": "gdrive"
            })
            logger.warning(f"   ❌ {error}")
        elif text and text.strip():
            documents[file['name']] = text
            logger.info(f"   ✅ Loaded {len(text)} characters.")
        else:
            errors.append({
                "file": file['name'],
                "error": "No text extracted",
                "type": "empty"
            })
            logger.warning(f"   ⚠️ No text extracted")

    logger.info(f"✅ Loaded {len(documents)} documents from GDrive. Errors: {len(errors)}")
    return documents, errors