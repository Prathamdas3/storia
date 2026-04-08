from datetime import date
import json
import random
import asyncio
import sys
from .constant import DATA_DIR, config, content_path, DefaultConfig, Mode
from .ai import generate_story, write_story
from .helper import write_config, get_random_topics


def reset() -> None:
    existing_key = None
    if config.exists():
        try:
            data = json.loads(config.read_text())
            existing_key = data.get("api_key")
        except (json.JSONDecodeError, FileNotFoundError):
            pass

    cfg = DefaultConfig(
        today=date.today().isoformat(),
        content=[],
        length=0,
        mode=Mode.TOPIC_BASED,
        api_key=existing_key,
    )
    write_config(cfg)


def setup() -> DefaultConfig:
    if not DATA_DIR.exists() or not DATA_DIR.is_dir():
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not config.exists():
        today = date.today().isoformat()
        try:
            with content_path.open("r") as f:
                content = json.load(f)
        except FileNotFoundError:
            print("Error: Vocabulary file not found.", file=sys.stderr)
            print(
                "Please ensure language files are installed correctly.", file=sys.stderr
            )
            sys.exit(1)
        except json.JSONDecodeError:
            print("Error: Vocabulary file is corrupted.", file=sys.stderr)
            print(f"Check the format of: {content_path}", file=sys.stderr)
            sys.exit(1)

        content_length = len(content)

        print("Welcome to Storia! Let's get you set up.")
        print("Please enter your Groq API key to continue.")
        print("(Get one free at https://groq.com)")
        from .api_key_manager import prompt_for_api_key

        api_key = prompt_for_api_key()

        cfg = DefaultConfig(
            today=today,
            content=[],
            length=content_length,
            mode=Mode.TOPIC_BASED,
            api_key=api_key,
        )
        write_config(cfg)
        return cfg
    else:
        try:
            with config.open("r") as f:
                config_data = json.load(f)
        except json.JSONDecodeError:
            print("Error: Config file is corrupted.", file=sys.stderr)
            print("Try running 'storia --reset' to fix this.", file=sys.stderr)
            sys.exit(1)

        return DefaultConfig(
            today=config_data["today"],
            content=config_data["content"],
            length=config_data["length"],
            mode=Mode(config_data["mode"]),
            api_key=config_data.get("api_key"),
        )


def get_daily_topics(data: DefaultConfig, n: int = 10) -> list[tuple[str, str]]:
    if not data.content:
        ids = get_random_topics(data.length, n)
        try:
            with content_path.open("r") as f:
                content = json.load(f)
        except FileNotFoundError:
            print("Error: Vocabulary file not found.", file=sys.stderr)
            print(
                "Please ensure language files are installed correctly.", file=sys.stderr
            )
            sys.exit(1)
        except json.JSONDecodeError:
            print("Error: Vocabulary file is corrupted.", file=sys.stderr)
            print(f"Check the format of: {content_path}", file=sys.stderr)
            sys.exit(1)

        data.content = [tuple(content[i].values()) for i in ids]
        update_config(data)
    return data.content


def update_config(config_data: DefaultConfig) -> None:
    write_config(config_data)


def main() -> None:
    try:
        config_data = setup()
    except SystemExit:
        raise
    except Exception as e:
        print(f"Unexpected error during setup: {e}", file=sys.stderr)
        print("Please try again or report this issue.", file=sys.stderr)
        sys.exit(1)

    if not config_data.api_key:
        print("API key not found in config. Let's add it now.")
        from .api_key_manager import prompt_for_api_key

        config_data.api_key = prompt_for_api_key()
        write_config(config_data)

    if config_data.today != date.today().isoformat():
        reset()

    try:
        if config_data.mode == Mode.RANDOM:
            if not config_data.content:
                print(
                    "No vocabulary words available. Switching to story mode.",
                    file=sys.stderr,
                )
                config_data.mode = Mode.TOPIC_BASED
            else:
                word, meaning = random.choice(config_data.content)
                print(f"{meaning} : {word}")
                config_data.mode = Mode.TOPIC_BASED
            update_config(config_data)
        elif config_data.mode == Mode.TOPIC_BASED:
            topics = get_daily_topics(config_data)
            story = asyncio.run(generate_story(topics))
            write_story(story, config_data.today)
            config_data.mode = Mode.RANDOM
            update_config(config_data)
    except IndexError as e:
        print("Error: No vocabulary words available.", file=sys.stderr)
        print("Generating a new story instead...", file=sys.stderr)
        try:
            topics = get_daily_topics(config_data)
            story = asyncio.run(generate_story(topics))
            write_story(story, config_data.today)
            config_data.mode = Mode.RANDOM
            update_config(config_data)
        except Exception as e:
            print(f"Failed to generate story: {e}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        print("Please try again.", file=sys.stderr)
        sys.exit(1)
