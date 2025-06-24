from google import genai
import os
# Ensure you have set the GOOGLE_API_KEY environment variable
cmd="YOU ARE A HELPFUL ASSISTANT. PLEASE ANSWER THE FOLLOWING QUESTION ALSO ADD A BYE AFTER YOU ARE COMPLETE: {prompt}"
def res(prompt: str):
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=cmd.format(prompt=prompt)
    )
    return response
