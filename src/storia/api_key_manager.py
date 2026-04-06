from .constant import config
import json


def get_api_key_from_config() -> str:
    """Read API key from config, raise if missing."""
    if not config.exists():
        raise ValueError("Config file not found. Run setup first.")

    try:
        data = json.loads(config.read_text())
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON in config file")

    key = data.get("api_key")
    if not key:
        raise ValueError("API key not set. Please configure your API key.")
    return key


def prompt_for_api_key() -> str:
    """Prompt user for API key with validation."""
    while True:
        key = input("Enter your Groq API key: ").strip()
        if not key:
            print("API key cannot be empty. Please try again.")
            continue
        if len(key) < 10:
            print("API key seems too short. Please check and try again.")
            continue
        return key


def get_or_prompt_api_key() -> str:
    """Get existing API key from config or prompt user if missing."""
    if config.exists():
        try:
            data = json.loads(config.read_text())
            if data.get("api_key"):
                return data["api_key"]
        except (json.JSONDecodeError, FileNotFoundError):
            pass

    print("API key not found. Please enter your Groq API key.")
    api_key = prompt_for_api_key()

    if config.exists():
        try:
            data = json.loads(config.read_text())
            data["api_key"] = api_key
            config.write_text(json.dumps(data, indent=2))
        except (json.JSONDecodeError, FileNotFoundError):
            pass

    return api_key
