import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini = genai.GenerativeModel("gemini-1.5-flash")

def generate_tweet_text(prompt: str, history: list = None):
    banned = ["kill", "hate", "violence", "nude", "nsfw", "bomb", "racist", "attack", "suicide"]
    if any(word in prompt.lower() for word in banned):
        return None, "Inappropriate content"

    context = ""
    if history:
        for msg in history[-10:]:
            if msg.get("prompt") and msg.get("tweet"):
                context += f"Prompt: {msg['prompt']}\nTweet: {msg['tweet']}\n"

    system_instruction = f"""
You are a creative and relatable tweet assistant. Write tweets in a witty, clever, or emotionally engaging human tone—like someone sharing a thought with friends online.

Instructions:
- Keep tone natural, humorous, empathetic, or sarcastic (not robotic)
- 1–3 natural-sounding hashtags at the end
- No "Not suitable for Twitter" responses
- Max 250 characters total

{context}
Prompt: {prompt}

Reply like this:
Tweet: ...
Hashtags: #example #example
"""

    try:
        gemini_response = gemini.generate_content(system_instruction).text.strip()
        print("[DEBUG] Gemini raw response:", gemini_response)

        tweet_match = re.search(r"Tweet:\s*(.*)", gemini_response)
        tags_match = re.search(r"Hashtags:\s*(.*)", gemini_response)

        tweet = tweet_match.group(1).strip() if tweet_match else gemini_response.strip()
        tags = tags_match.group(1).strip() if tags_match else ""

        full = f"{tweet} {tags}".strip()

        if len(tweet) < 10:
            return None, "Tweet too short or unclear."

        if len(full) > 280:
            full = full[:277].rsplit(" ", 1)[0] + "..."

        return full, None

    except Exception as e:
        return None, f"Gemini generation failed: {str(e)}"
