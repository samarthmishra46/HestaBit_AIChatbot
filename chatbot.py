from google import genai
import os

cmd = """YOU ARE A HELPFUL ASSISTANT. ANSWER BASED ON PREVIOUS CONVERSATION BELOW:\n
{history}

USER: {prompt}
ASSISTANT:"""

def res(prompt: str, history: list[str] = []):
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    history_text = "\n".join(history)
    final_prompt = cmd.format(history=history_text, prompt=prompt)

    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=final_prompt
    )
    return response
