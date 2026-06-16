import requests

from config.settings import (
    ELEVENLABS_API_KEY,
    ELEVENLABS_VOICE_ID,
)

def generate_voice(
    text: str,
    output_path: str,
):
    url = (
        "https://api.elevenlabs.io/v1/text-to-speech/"
        f"{ELEVENLABS_VOICE_ID}"
    )

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers,
    )

    response.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(response.content)

    return output_path