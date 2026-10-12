
import requests
import time

API_URL = "http://localhost:11434/v1/chat/completions"

payload = {
    "model": "fee-assistant",
    "messages": [
        {
            "role": "system",
            "content": (
                "You are a friendly AI tutor. "
                "Explain concepts in exactly two short sentences."
            )
        },
        {
            "role": "user",
            "content": "What is machine learning?"
        }
    ],
    "stream": False,
    "temperature": 0
}

start_time = time.perf_counter()

response = requests.post(
    API_URL,
    json=payload,
    headers={"Authorization": "Bearer ollama"},
    timeout=120
)

response.raise_for_status()
result = response.json()

end_time = time.perf_counter()

answer = result["choices"][0]["message"]["content"]

print("=== OPENAI-COMPATIBLE API TEST ===")
print("Model:", result.get("model"))
print("Response:", answer)
print(f"Total time: {end_time - start_time:.3f} seconds")
print("Endpoint:", API_URL)
