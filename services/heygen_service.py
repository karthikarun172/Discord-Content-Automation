import requests

from config.settings import (
    HEYGEN_API_KEY,
    HEYGEN_AVATAR_ID,
)
import time

def upload_audio(audio_path):

    with open(audio_path, "rb") as f:

        response = requests.post(
            "https://api.heygen.com/v3/assets",
            headers={
                "x-api-key": HEYGEN_API_KEY
            },
            files={
                "file": f
            }
        )

    response.raise_for_status()

    return response.json()["data"]["asset_id"]

def create_video(audio_asset_id):

    payload = {
        "type": "avatar",
        "avatar_id": HEYGEN_AVATAR_ID,
        "audio_asset_id": audio_asset_id,
    }

    response = requests.post(
        "https://api.heygen.com/v3/videos",
        headers={
            "x-api-key": HEYGEN_API_KEY,
            "Content-Type": "application/json",
        },
        json=payload,
    )

    response.raise_for_status()

    return response.json()["data"]["video_id"]

def wait_for_video(video_id):

    while True:

        response = requests.get(
            f"https://api.heygen.com/v3/videos/{video_id}",
            headers={
                "x-api-key": HEYGEN_API_KEY,
            },
        )

        response.raise_for_status()

        data = response.json()["data"]

        status = data["status"]

        if status == "completed":
            return data["video_url"]

        if status == "failed":
            raise Exception(
                data.get(
                    "failure_message",
                    "Video generation failed"
                )
            )

        time.sleep(10)

def download_video(
    video_url,
    output_path,
):

    response = requests.get(video_url)

    response.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(response.content)

    return output_path

def generate_avatar_video(
    audio_path,
    output_path,
):

    asset_id = upload_audio(audio_path)

    video_id = create_video(asset_id)

    video_url = wait_for_video(video_id)

    return download_video(
        video_url,
        output_path,
    )