from google import genai
import os
import memory_vector
import memory_redis

cmd = """YOU ARE A HELPFUL ASSISTANT. HERE IS THE CONTEXT:\n
SHORT-TERM MEMORY:\n{short_term}\n
LONG-TERM MEMORY:\n{long_term}\n
NOW ANSWER THIS:\n
USER: {prompt}
ASSISTANT:"""

def res(prompt: str, session_id: str):
    # Load both types of memory
    short_term = memory_redis.get_history(session_id)
    long_term = memory_vector.retrieve_relevant(prompt)

    # Format context
    final_prompt = cmd.format(
        short_term="\n".join(short_term),
        long_term="\n".join(long_term),
        prompt=prompt
    )

    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=final_prompt
    )

    # Store short-term and long-term memories
    memory_redis.update_history(session_id, prompt, response.text)
    memory_vector.store_memory(f"USER: {prompt}")
    memory_vector.store_memory(f"ASSISTANT: {response.text}")

    return response
