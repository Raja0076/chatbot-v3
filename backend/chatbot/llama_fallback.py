import os
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

print(f"[Groq] Initializing with model: {GROQ_MODEL}")
print(f"[Groq] API key loaded: {'YES' if GROQ_API_KEY else 'NO - check your .env file'}")

client = Groq(api_key=GROQ_API_KEY)
print("[Groq] Client created successfully.")

CAREER_SYSTEM_PROMPT = (
    "You are a student career assistant. "
    "Only answer about career development, internships, resumes, interviews, skills, and education. "
    "If the question is unrelated, politely bring it back to career guidance. "
    "Keep answers concise and helpful."
)


def get_llama_response(question, chat_history=None):
    """
    Uses Groq cloud API instead of local Qwen2.
    Drop-in replacement — same function signature.
    """
    print(f"\n[Groq] Received question: {question}")

    messages = [{"role": "system", "content": CAREER_SYSTEM_PROMPT}]
    print("[Groq] System prompt added.")

    # Add chat history (last 6 turns)
    if chat_history and isinstance(chat_history, list):
        history_to_use = chat_history[-6:]
        print(f"[Groq] Chat history found: {len(chat_history)} total turns, using last {len(history_to_use)}.")
        for turn in history_to_use:
            if isinstance(turn, dict) and "role" in turn and "content" in turn:
                messages.append({"role": turn["role"], "content": turn["content"]})
                print(f"[Groq]   Added history turn -> role: {turn['role']} | content: {turn['content'][:60]}...")
    else:
        print("[Groq] No chat history provided.")

    messages.append({"role": "user", "content": question})
    print(f"[Groq] Final message count sent to API: {len(messages)}")

    try:
        print(f"[Groq] Sending request to model: {GROQ_MODEL} ...")
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            max_tokens=512,
            temperature=0.7,
        )

        result = response.choices[0].message.content.strip()
        print(f"[Groq] Response received successfully.")
        print(f"[Groq] Tokens used — prompt: {response.usage.prompt_tokens}, "
              f"completion: {response.usage.completion_tokens}, "
              f"total: {response.usage.total_tokens}")
        print(f"[Groq] Final output: {result}")
        return result

    except Exception as exc:
        print(f"[Groq] ERROR: {type(exc).__name__}: {exc}")
        print("[Groq] Returning None — check API key, model name, or network connection.")
        return None