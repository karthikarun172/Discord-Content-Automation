from google import genai
from google.genai import types

from config.settings import GEMINI_API_KEY
from prompts import DOCUMENTARY_BLUEPRINT
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
# import asyncio
# import random

# from utils.logger import logger

# async def generate_content_with_retry(
#     client,
#     model,
#     contents,
#     config,
#     max_attempts=5,
# ):
#     """
#     Retry Gemini requests using exponential backoff.

#     Delays:
#     1s -> 2s -> 4s -> 8s -> 16s
#     """

#     for attempt in range(max_attempts):
#         try:
#             return await asyncio.to_thread(
#                 lambda: client.models.generate_content(
#                     model=model,
#                     contents=contents,
#                     config=config,
#                 )
#             )

#         except Exception as e:

#             error_text = str(e)

#             retryable_errors = [
#                 "503",
#                 "UNAVAILABLE",
#                 "RESOURCE_EXHAUSTED",
#                 "429",
#             ]

#             should_retry = any(
#                 err in error_text
#                 for err in retryable_errors
#             )

#             if not should_retry:
#                 raise

#             if attempt == max_attempts - 1:
#                 raise

#             wait_time = (2 ** attempt) + random.uniform(0, 1)

#             logger.info(
#                 f"Gemini retry "
#                 f"{attempt + 1}/{max_attempts} "
#                 f"after {wait_time:.2f}s"
#             )

#             await asyncio.sleep(wait_time)