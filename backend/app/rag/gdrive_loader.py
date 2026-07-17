# backend/app/rag/gdrive_loader.py

import tempfile
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any, Callable

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from app.rag.loader import _handle_pdf, _handle_docx, _handle_txt

logger = logging.getLogger(__name__)

# Path to your service account JSON file
SERVICE_ACCOUNT_FILE = Path(__file__).parent.parent.parent / "gdrive_credentials.json"
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

_HANDLERS: Dict[str, Callable[[Path], str]] = {
    ".pdf": _handle_pdf,
    ".docx": _handle_docx,
    ".txt": _handle_txt,
}
SUPPORTED_EXTENSIONS = set(_HANDLERS.keys())

_folder_name_cache: Dict[str, str] = {}


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


def _get_folder_name(service, folder_id: str) -> str:
    """Get folder name by ID, with caching."""
    if folder_id in _folder_name_cache:
        return _folder_name_cache[folder_id]
    
    try:
        folder = service.files().get(fileId=folder_id, fields='name').execute()
        name = folder.get('name', 'Unknown')
        _folder_name_cache[folder_id] = name
        return name
    except Exception as e:
        logger.error(f"Error fetching folder name for {folder_id}: {e}")
        return "Unknown"


def _get_file_hierarchy(service, file_id: str) -> List[str]:
    """
    Traverse the folder tree upwards to get the full path of a file.
    Returns a list like: ['Department_A', 'Engineering'] or [] if root.
    """
    hierarchy = []
    try:
        file_meta = service.files().get(fileId=file_id, fields='parents').execute()
        parents = file_meta.get('parents', [])
        
        if not parents:
            return hierarchy
        
        parent_id = parents[0]
        
        while parent_id:
            folder_meta = service.files().get(
                fileId=parent_id, 
                fields='name, parents'
            ).execute()
            
            folder_name = folder_meta.get('name', '')
            if folder_name:
                hierarchy.insert(0, folder_name)
            
            parent_id = folder_meta.get('parents', [None])[0]
            
    except Exception as e:
        logger.error(f"Error walking hierarchy for file {file_id}: {e}")
    
    return hierarchy


def list_files_recursively(service, folder_id: str) -> List[Dict]:
    """
    Recursively list all files (not folders) inside a Google Drive folder
    and all its subfolders.
    """
    results = []
    page_token = None
    
    # 1. List all files directly in this folder
    while True:
        response = service.files().list(
            q=f"'{folder_id}' in parents and mimeType!='application/vnd.google-apps.folder'",
            spaces='drive',
            fields='nextPageToken, files(id, name, mimeType, parents)',
            pageToken=page_token
        ).execute()
        results.extend(response.get('files', []))
        page_token = response.get('nextPageToken')
        if not page_token:
            break
    
    # 2. List all subfolders in this folder
    page_token = None
    while True:
        response = service.files().list(
            q=f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.folder'",
            spaces='drive',
            fields='nextPageToken, files(id, name, mimeType)',
            pageToken=page_token
        ).execute()
        subfolders = response.get('files', [])
        page_token = response.get('nextPageToken')
        
        # 3. Recursively list files in each subfolder
        for folder in subfolders:
            subfolder_files = list_files_recursively(service, folder['id'])
            results.extend(subfolder_files)
        
        if not page_token:
            break
    
    return results


def download_and_extract_file(service, file_id: str, file_name: str) -> Tuple[str, str]:
    """
    Downloads a file from GDrive to a temporary file, extracts text,
    and cleans up the temp file. Returns (extracted_text, error_message).
    """
    ext = Path(file_name).suffix.lower()
    
    if ext not in SUPPORTED_EXTENSIONS:
        return "", f"Unsupported file type: {ext}"

    handler = _HANDLERS[ext]

    temp_file = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
    temp_path = Path(temp_file.name)

    try:
        request = service.files().get_media(fileId=file_id)
        downloader = MediaIoBaseDownload(temp_file, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()

        temp_file.close()

        text = handler(temp_path)

        if not text or not text.strip():
            return "", "No text extracted"

        return text, ""

    except Exception as e:
        logger.error(f"Error processing {file_name}: {e}")
        return "", str(e)

    finally:
        if temp_path.exists():
            temp_path.unlink()


def load_documents_from_gdrive(folder_id: str) -> Tuple[List[Dict[str, Any]], List[Dict]]:
    """
    Main function: Load all supported documents from a Google Drive folder
    and all its subfolders (recursive).
    """
    service = get_drive_service()
    files = list_files_recursively(service, folder_id)

    if not files:
        logger.warning(f"No files found in folder ID: {folder_id}")
        return [], []

    documents = []
    errors = []

    logger.info(f"📁 Found {len(files)} files in GDrive folder (including subfolders).")

    for file in files:
        file_name = file['name']
        file_id = file['id']
        
        logger.info(f"📄 Processing: {file_name}")

        hierarchy = _get_file_hierarchy(service, file_id)
        
        if len(hierarchy) >= 2:
            department = hierarchy[-2]
            role = hierarchy[-1]
        else:
            department = "Unknown"
            role = "Unknown"
            logger.warning(f"File {file_name} has shallow hierarchy: {hierarchy}")

        text, error = download_and_extract_file(service, file_id, file_name)

        if error:
            errors.append({"file": file_name, "error": error, "type": "gdrive"})
            logger.warning(f"   ❌ {error}")
        elif text and text.strip():
            documents.append({
                "file_name": file_name,
                "text": text,
                "department": department,
                "role": role
            })
            logger.info(f"   ✅ Loaded {len(text)} chars | Dept: {department} | Role: {role}")
        else:
            errors.append({"file": file_name, "error": "No text extracted", "type": "empty"})
            logger.warning(f"   ⚠️ No text extracted")

    logger.info(f"✅ Loaded {len(documents)} docs. Errors: {len(errors)}")
    return documents, errors