from groq import AsyncGroq
from .constant import api_key, Stories
from .prompt import prompt_text

client=AsyncGroq(
    api_key=api_key
)

def organize_content(content:list[tuple[str,str]])->list[str]:
    words:list[str]=[]
    for i,_ in content:
        words.append(i)

    return words 

async def generate_story(topics:list[tuple[str,str]])->str:
    try:
        words=organize_content(topics)
        response=await client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role":"system",
                    "content":prompt_text
                },
                {
                    "role":"user",
                    "content":f"Target language: Italian\nWord list: {words}"
                }
            ],
            temperature=1,
            max_tokens=4000,
            top_p=.95
        )
        story = response.choices[0].message.content
        if not story:
            raise Exception("Error generating story")
        return story
    except Exception as e:
        print("Error generating story:", e)
        return ""
    
def write_story(story:str,date:str):
    parts = story.split("\n\n", 1)

    if len(parts) != 2:
        raise ValueError("Unexpected response format from model")

    target_language_story = parts[0]
    english_retelling = parts[1]
    print(f"--------\n"
            f"[{date}]\n\n"
            f"{target_language_story}\n\n"
            f"{english_retelling}\n"
            f"--------\n\n"
            )
    with Stories.open( "a", encoding="utf-8") as f:
        f.write(
            f"--------\n"
            f"[{date}]\n\n"
            f"{target_language_story}\n\n"
            f"{english_retelling}\n"
            f"--------\n\n"
        )