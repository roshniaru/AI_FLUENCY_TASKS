
import requests
import time
import json

API_URL = "http://localhost:11434/api/generate"

payload = {
    "model": "fee-assistant",
    "prompt": "Explain artificial intelligence in three short sentences.",
    "stream": True
}

start_time = time.perf_counter()
first_token_time = None
full_response = ""
final_data = {}

print("=== OLLAMA STREAMING API TEST ===")
print("Response: ", end="", flush=True)

with requests.post(
    API_URL, json=payload, stream=True, timeout=120
) as response:
    response.raise_for_status()

    for line in response.iter_lines():
        if not line:
            continue

        data = json.loads(line)

        if data.get("response"):
            if first_token_time is None:
                first_token_time = time.perf_counter()

            chunk = data["response"]
            full_response += chunk
            print(chunk, end="", flush=True)

        if data.get("done"):
            final_data = data

end_time = time.perf_counter()

print("\n\n=== PERFORMANCE ===")

if first_token_time is not None:
    ttft = first_token_time - start_time
    print(f"TTFT: {ttft:.3f} seconds")
else:
    print("TTFT: No response token received")

total_time = end_time - start_time
print(f"Total time: {total_time:.3f} seconds")

eval_count = final_data.get("eval_count", 0)
eval_duration = final_data.get("eval_duration", 0)

if eval_duration > 0:
    tokens_per_second = eval_count / (eval_duration / 1_000_000_000)
    print(f"Generation speed: {tokens_per_second:.2f} tokens/sec")
else:
    print("Generation speed: Not available")

print(f"Generated tokens: {eval_count}")
