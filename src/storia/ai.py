from groq import AsyncGroq
from .constant import Stories
from .api_key_manager import get_api_key_from_config
from .prompt import prompt_text
import sys


def get_client() -> AsyncGroq:
    """Get Groq client with API key from config."""
    api_key = get_api_key_from_config()
    return AsyncGroq(api_key=api_key)


async def generate_story(topics: list[tuple[str, str]]) -> str:
    client = get_client()
    models = ["openai/gpt-oss-20b", "llama-3.3-70b-versatile"]

    last_error = None
    for model in models:
        try:
            words = [word for word, _ in topics]
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": prompt_text},
                    {
                        "role": "user",
                        "content": f"Target language: Italian\nWord list: {words}",
                    },
                ],
                temperature=1,
                max_tokens=4000,
                top_p=0.95,
            )
            story = response.choices[0].message.content
            if story:
                return story
        except Exception as e:
            last_error = str(e)
            print(f"Model {model} failed: {e}", file=sys.stderr)
            continue

    print("Error: All AI models failed to generate a story.", file=sys.stderr)
    print(f"Last error: {last_error}", file=sys.stderr)
    print("Please check your API key and try again.", file=sys.stderr)
    sys.exit(1)


def write_story(story: str, date: str) -> None:
    parts = story.split("\n\n", 1)

    if len(parts) != 2:
        print("Error: AI returned an unexpected response format.", file=sys.stderr)
        print(
            "The story must have two parts separated by a blank line.", file=sys.stderr
        )
        print("Please try again.", file=sys.stderr)
        sys.exit(1)

    target_language_story = parts[0]
    english_retelling = parts[1]
    output = (
        f"--------\n"
        f"[{date}]\n\n"
        f"{target_language_story}\n\n"
        f"{english_retelling}\n"
        f"--------\n\n"
    )
    print(output)
    try:
        with Stories.open("a", encoding="utf-8") as f:
            f.write(output)
    except FileNotFoundError:
        print("Error: Could not save story to file.", file=sys.stderr)
        print(f"Check that the directory exists: {Stories.parent}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to save story: {e}", file=sys.stderr)
        sys.exit(1)
