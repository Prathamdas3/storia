from groq import AsyncGroq
from .constant import api_key, Stories
from .prompt import prompt_text

client = AsyncGroq(api_key=api_key)


async def generate_story(topics: list[tuple[str, str]]) -> str:
    models = ["openai/gpt-oss-20b", "llama-3.3-70b-versatile"]

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
            print(f"Model {model} failed: {e}")
            continue

    raise Exception("All models failed to generate story")


def write_story(story: str, date: str) -> None:
    parts = story.split("\n\n", 1)

    if len(parts) != 2:
        raise ValueError("Unexpected response format from model")

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
    with Stories.open("a", encoding="utf-8") as f:
        f.write(output)
