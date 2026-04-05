from pathlib import Path
from importlib.resources import files
import os
from dotenv import load_dotenv
from dataclasses import dataclass
from enum import Enum

load_dotenv()

HOME = Path.home()
DATA_DIR = HOME / ".storia"
config = DATA_DIR / "config.json"
Stories = DATA_DIR / "stories.txt"
content_path = files("storia.languages").joinpath("italian.json")
api_key = os.environ.get("API_KEY", "")
if not api_key:
    raise EnvironmentError("API_KEY not set. Create .env file with your Groq API key.")


class Mode(Enum):
    RANDOM = 0
    TOPIC_BASED = 1


@dataclass
class DefaultConfig:
    today: str
    content: list
    length: int
    mode: Mode
