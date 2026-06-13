import logging
import os

LOG_LEVEL = os.getenv("LOG_LEVEL","INFO")

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("decisionforge")