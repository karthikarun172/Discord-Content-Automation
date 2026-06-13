from services.googe_services import (
    get_google_services
)

from config.settings import (
    GOOGLE_DRIVE_FOLDER_ID
)

from utils.logger import logger


def push_workspace_to_docs(title, structural_text):
    """
    Builds a structured asset document via Google Cloud, embeds 
    open-source visual illustrations, and saves it into the video assets root.
    """
    try:
        docs_service, drive_service = get_google_services()
        print("STEP 1: Creating document")
        
        # Step 1: Create empty baseline document template file
        doc_meta = {'title': f"{title} - Production Blueprint"}
        doc = docs_service.documents().create(body=doc_meta).execute()
        doc_id = doc.get('documentId')
        print(f"Created Doc ID: {doc_id}")
        # Append standard text headers safely to document timeline body
        body_content = structural_text + "\n\n--- AUTO-GENERATED STORYBOARD BLUEPRINT ---\n\n"
        requests_payload = [{
            'insertText': {
                'location': {'index': 1},
                'text': body_content
            }
        }]
        docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests_payload}).execute()
        
        # Step 2: File document inside shared project folder
        print(f"Folder ID: {GOOGLE_DRIVE_FOLDER_ID}")
        if GOOGLE_DRIVE_FOLDER_ID and GOOGLE_DRIVE_FOLDER_ID != "YOUR_FOLDER_ID":
            file_meta = drive_service.files().get(fileId=doc_id, fields='parents').execute()
            previous_parents = ",".join(file_meta.get('parents', []))
            drive_service.files().update(
                fileId=doc_id,
                addParents=GOOGLE_DRIVE_FOLDER_ID,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()
            print("Document moved successfully")
            
        return f"https://docs.google.com/document/d/{doc_id}/edit"
    except Exception as e:
        logger.info(f"Document compilation failed with error {str(e)}")
        return None
