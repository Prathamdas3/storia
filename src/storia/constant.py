from pathlib import Path
from importlib.resources import files
import os
from dotenv import load_dotenv

load_dotenv()

HOME = Path.home()
DATA_DIR = HOME / ".storia"
config = DATA_DIR / "config.json"
Stories=DATA_DIR / "stories.txt"
content_path = files("storia.languages").joinpath("italian.json")
api_key=os.environ.get("API_KEY","")