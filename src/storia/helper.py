import json
import random
from .constant import config, DATA_DIR, DefaultConfig


def config_to_dict(cfg: DefaultConfig) -> dict:
    return {
        "today": cfg.today,
        "content": cfg.content,
        "length": cfg.length,
        "mode": cfg.mode.value,
        "api_key": cfg.api_key,
    }


def write_config(cfg: DefaultConfig, preserve_api_key: bool = True) -> None:
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    if preserve_api_key and config.exists():
        try:
            existing = json.loads(config.read_text())
        except (json.JSONDecodeError, FileNotFoundError):
            existing = {}

        # Update with new values, but only include api_key if it's not None
        new_data = config_to_dict(cfg)
        if cfg.api_key is None:
            new_data.pop("api_key", None)
        existing.update(new_data)
    else:
        existing = config_to_dict(cfg)

    config.write_text(json.dumps(existing, indent=2))


def get_random_topics(length: int, n: int = 10) -> list[int]:
    return [random.randint(0, length - 1) for _ in range(n)]
