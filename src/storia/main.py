from datetime import date
import json
import random
import asyncio
from dataclasses import dataclass
from enum import Enum
from .constant import DATA_DIR, config, content_path
from .ai import generate_story, write_story


class Mode(Enum):
    RANDOM = 0
    TOPIC_BASED = 1


@dataclass
class DefaultConfig:
    today: str
    content: list
    length: int
    mode: Mode



def get_random_topics(length: int, n=10)->list[int]:
    ids = []
    for _ in range(n):
        ids.append(random.randint(0, length - 1))
    return ids


def reset():
    with config.open("w") as f:
        json.dump(
            {
                "today": date.today().isoformat(),
                "content": [],
                "length": 0,
                "mode": Mode.TOPIC_BASED.value, 
            },
            f,
        )


def setup() -> DefaultConfig:
    if not DATA_DIR.exists() or not DATA_DIR.is_dir():
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not config.exists():
        today = date.today().isoformat()
        with content_path.open("r") as f:
            content = json.load(f)
        content_length = len(content)

        with config.open("w") as f:
            json.dump(
                {
                    "today": today,
                    "content": [],
                    "length": content_length,
                    "mode": Mode.TOPIC_BASED.value,
                },
                f,
            )

        return DefaultConfig(
            today=today, content=[], length=content_length, mode=Mode.TOPIC_BASED
        )
    else:
        with config.open("r") as f:
            config_data = json.load(f)

        return DefaultConfig(
            today=config_data["today"],
            content=config_data["content"],
            length=config_data["length"],
            mode=Mode(config_data["mode"]),
        )


def get_random_word(words:list[dict[str, str]]) -> dict[str, str]:
    return random.choice(words)


def get_daily_topics(data: DefaultConfig, n: int = 10)->list[tuple[str,str]]:
    if not data.content:
        ids=get_random_topics(data.length,n)
        with content_path.open("r") as f:
            content= json.load(f)
        data.content=[tuple(content[i].values()) for i in ids]
        update_config(data)
    return data.content
    

def update_config(config_data: DefaultConfig):
    with config.open("w") as f:
        json.dump(
            {
                "today": config_data.today,
                "content": config_data.content,
                "length": config_data.length,
                "mode": config_data.mode.value,
            },
            f,
        )

def main():
    config_data = setup()
    if config_data.today != date.today().isoformat():
        reset()
    if config_data.mode == Mode.RANDOM:
        word,meaning = get_random_word(config_data.content)
        print(f"{meaning} : {word}")
        config_data.mode = Mode.TOPIC_BASED
        update_config(config_data)
    elif config_data.mode == Mode.TOPIC_BASED:
        topics=get_daily_topics(config_data)
        story=asyncio.run(generate_story(topics))
        if story is None:
            raise ValueError("generate_story returned None")
        write_story(story,config_data.today)
        config_data.mode = Mode.RANDOM
        update_config(config_data)
        