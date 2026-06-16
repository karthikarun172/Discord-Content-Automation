from googleapiclient.http import MediaFileUpload

from services.google_services import (
    get_google_services
)

from config.settings import (
    GOOGLE_DRIVE_FOLDER_ID
)


def upload_audio_to_drive(file_path):

    _, drive_service = get_google_services()

    file_metadata = {
        "name": file_path.split("/")[-1],
        "parents": [GOOGLE_DRIVE_FOLDER_ID],
    }

    media = MediaFileUpload(
        file_path,
        mimetype="audio/mpeg"
    )

    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, webViewLink"
    ).execute()

    return file["webViewLink"]