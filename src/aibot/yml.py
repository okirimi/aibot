from pathlib import Path

import yaml

with (
    Path(__file__).parents[2].joinpath("prompts", ".prompt.sample.yml").open(encoding="utf-8") as f
):
    prompt = yaml.safe_load(f)

CHAT_SYSTEM_DEFAULT: str = prompt.get("chat_default", "")
FIXPY_SYSTEM: str = prompt.get("fixpy", "")
