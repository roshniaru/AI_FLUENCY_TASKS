
AVAILABLE_MEMORY_GB = 8.0
RUNTIME_OVERHEAD_GB = 0.8
KV_BYTES = 2
GB = 1_000_000_000

MODELS = [
    {
        "name": "Llama 3.2 1B",
        "params": 1.23,
        "layers": 16,
        "kv_heads": 8,
        "head_dim": 64,
    },
    {
        "name": "Llama 3.2 3B",
        "params": 3.21,
        "layers": 28,
        "kv_heads": 8,
        "head_dim": 128,
    },
    {
        "name": "Qwen2.5 3B",
        "params": 3.09,
        "layers": 36,
        "kv_heads": 2,
        "head_dim": 128,
    },
    {
        "name": "Gemma 3 4B",
        "params": 3.88,
        "layers": 34,
        "kv_heads": 4,
        "head_dim": 256,
    },
]

QUANT_BYTES = {
    "Q4_K_M": 0.62,
    "Q5_K_M": 0.70,
    "Q8_0": 1.00,
    "FP16": 2.00,
}


def estimate_memory(model, context, quantization):
    weights_gb = model["params"] * QUANT_BYTES[quantization]

    kv_gb = (
        2
        * model["layers"]
        * model["kv_heads"]
        * model["head_dim"]
        * context
        * KV_BYTES
        / GB
    )

    total_gb = (
        weights_gb
        + kv_gb
        + RUNTIME_OVERHEAD_GB
    )

    return {
        "weights": weights_gb,
        "kv_cache": kv_gb,
        "total": total_gb,
        "fits": total_gb <= AVAILABLE_MEMORY_GB,
    }


def main():
    print("DAY 4 - LLM MEMORY ESTIMATOR")
    print("Available memory:", AVAILABLE_MEMORY_GB, "GB")
    print("Context: 4096 tokens")
    print("Quantization: Q4_K_M")
    print("-" * 90)

    for model in MODELS:
        result = estimate_memory(
            model,
            context=4096,
            quantization="Q4_K_M",
        )

        verdict = "YES" if result["fits"] else "NO"

        print("\nModel:", model["name"])
        print("Parameters:", model["params"], "B")
        print("Weights:", round(result["weights"], 3), "GB")
        print("KV cache:", round(result["kv_cache"], 3), "GB")
        print("Runtime overhead:", RUNTIME_OVERHEAD_GB, "GB")
        print("Total:", round(result["total"], 3), "GB")
        print("Fits in memory:", verdict)


if __name__ == "__main__":
    main()
