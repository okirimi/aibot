from pathlib import Path

import yaml

with (
    Path(__file__).parents[2].joinpath("resources", "system_instructions.yml").open(encoding="utf-8") as f
):
    prompt = yaml.safe_load(f)

CHAT_SYSTEM_DEFAULT: str = prompt.get("chat", "")
FIXPY_SYSTEM: str = prompt.get("fixpy", "")
