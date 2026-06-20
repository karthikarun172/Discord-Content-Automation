# prompts/__init__.py

from pathlib import Path

PROMPT_DIR = Path(__file__).parent

with open(
    PROMPT_DIR / "documentary_blueprint.txt",
    encoding="utf-8"
) as f:
    DOCUMENTARY_BLUEPRINT = f.read()

with open(
    PROMPT_DIR / "storyboard.txt",
    encoding="utf-8"
) as f:
    STORYBOARD_PROMPT = f.read()