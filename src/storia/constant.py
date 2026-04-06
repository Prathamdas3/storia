from pathlib import Path
from importlib.resources import files
from dataclasses import dataclass
from enum import Enum

HOME = Path.home()
DATA_DIR = HOME / ".storia"
config = DATA_DIR / "config.json"
Stories = DATA_DIR / "stories.txt"
content_path = files("storia.languages").joinpath("italian.json")


class Mode(Enum):
    RANDOM = 0
    TOPIC_BASED = 1


@dataclass
class DefaultConfig:
    today: str
    content: list
    length: int
    mode: Mode
    api_key: str | None = None
