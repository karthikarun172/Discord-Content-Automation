import asyncio
import random

from utils.logger import logger


async def retry_async(
    func,
    max_attempts=5
):

    for attempt in range(max_attempts):

        try:
            return await asyncio.to_thread(func)

        except Exception as e:

            error_text = str(e)

            retryable_errors = [
                "503",
                "UNAVAILABLE",
                "RESOURCE_EXHAUSTED",
                "429",
            ]

            if not any(
                err in error_text
                for err in retryable_errors
            ):
                raise

            if attempt == max_attempts - 1:
                raise

            wait_time = (
                2 ** attempt
            ) + random.uniform(0, 1)

            logger.warning(
                f"Retry {attempt + 1}/{max_attempts}"
            )

            await asyncio.sleep(wait_time)