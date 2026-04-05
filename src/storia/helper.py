import json
import random
from .constant import config, DefaultConfig


def config_to_dict(cfg: DefaultConfig) -> dict:
    return {
        "today": cfg.today,
        "content": cfg.content,
        "length": cfg.length,
        "mode": cfg.mode.value,
    }


def write_config(cfg: DefaultConfig) -> None:
    with config.open("w") as f:
        json.dump(config_to_dict(cfg), f)


def get_random_topics(length: int, n: int = 10) -> list[int]:
    return [random.randint(0, length - 1) for _ in range(n)]
