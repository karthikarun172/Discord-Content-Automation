from google import genai
from google.genai import types

from config.settings import GEMINI_API_KEY
from prompts import (
    DOCUMENTARY_BLUEPRINT,
    STORYBOARD_PROMPT
)
from utils.retry import retry_async

client = genai.Client(api_key=GEMINI_API_KEY)


async def _generate_content(
    model,
    contents,
    config,
):
    return await retry_async(
        lambda: client.models.generate_content(
            model=model,
            contents=contents,
            config=config,
        )
    )


async def generate_documentary_blueprint(
    topic_prompt: str,
):
    response = await _generate_content(
        model="gemini-2.5-flash-lite",
        contents=(
            "Develop a comprehensive high-retention "
            f"video documentary script configuration "
            f"from scratch covering this concept: "
            f"{topic_prompt}"
        ),
        config=types.GenerateContentConfig(
            system_instruction=DOCUMENTARY_BLUEPRINT,
            temperature=0.7,
            max_output_tokens=8192,
        ),
    )

    return response.text

async def optimize_script(
    raw_script_block: str,
):
    response = await _generate_content(
        model="gemini-2.5-flash",
        contents=(
            "Analyze this pasted rough content "
            "text block, align its storytelling "
            "pacing to our guidelines:\n\n"
            f"{raw_script_block}"
        ),
        config=types.GenerateContentConfig(
            system_instruction=DOCUMENTARY_BLUEPRINT,
            temperature=0.3,
        ),
    )

    return response.text

async def generate_storyboard(
    script_text: str,
):
    response = await _generate_content(
        model="gemini-2.5-flash",
        contents=script_text,
        config=types.GenerateContentConfig(
            system_instruction=STORYBOARD_PROMPT,
            temperature=0.2,
        ),
    )

    return response.text