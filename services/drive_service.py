from googleapiclient.http import MediaFileUpload
import os

from services.google_services import (
    get_google_services
)

from config.settings import (
    GOOGLE_DRIVE_FOLDER_ID
)


def upload_file_to_drive(
    file_path,
    mime_type=None,
):

    _, drive_service = get_google_services()

    file_metadata = {
        "name": os.path.basename(file_path),
        "parents": [GOOGLE_DRIVE_FOLDER_ID],
    }

    media = MediaFileUpload(
        file_path,
        mimetype=mime_type,
        resumable=True,
    )

    file = (
        drive_service.files()
        .create(
            body=file_metadata,
            media_body=media,
            fields="id, webViewLink",
        )
        .execute()
    )

    return file["webViewLink"]

import os


def upload_project_assets(
    project_path,
):
    uploaded_links = []

    for root, _, files in os.walk(
        project_path
    ):

        for file_name in files:

            file_path = os.path.join(
                root,
                file_name
            )

            link = upload_file_to_drive(
                file_path
            )

            uploaded_links.append(
                link
            )

    return uploaded_links