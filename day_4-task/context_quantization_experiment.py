
from memory_estimator import (
    MODELS,
    QUANT_BYTES,
    AVAILABLE_MEMORY_GB,
    estimate_memory,
)


def main():
    model = next(
        m for m in MODELS
        if m["name"] == "Llama 3.2 3B"
    )

    print("DAY 4 - CONTEXT AND QUANTIZATION EXPERIMENT")
    print("Model:", model["name"])
    print("Available memory:", AVAILABLE_MEMORY_GB, "GB")

    # Experiment A: Change context length
    print("\nA) CONTEXT LENGTH EXPERIMENT")
    print("Quantization fixed at Q4_K_M")
    print("-" * 75)

    for context in [1024, 2048, 4096, 8192]:
        result = estimate_memory(
            model,
            context=context,
            quantization="Q4_K_M",
        )

        print(
            f"Context: {context:5d} tokens | "
            f"Weights: {result['weights']:.3f} GB | "
            f"KV cache: {result['kv_cache']:.3f} GB | "
            f"Total: {result['total']:.3f} GB | "
            f"Fits: {'YES' if result['fits'] else 'NO'}"
        )

    # Experiment B: Change quantization
    print("\nB) QUANTIZATION EXPERIMENT")
    print("Context fixed at 4096 tokens")
    print("-" * 75)

    for quantization in QUANT_BYTES:
        result = estimate_memory(
            model,
            context=4096,
            quantization=quantization,
        )

        print(
            f"Quantization: {quantization:8s} | "
            f"Weights: {result['weights']:.3f} GB | "
            f"KV cache: {result['kv_cache']:.3f} GB | "
            f"Total: {result['total']:.3f} GB | "
            f"Fits: {'YES' if result['fits'] else 'NO'}"
        )


if __name__ == "__main__":
    main()
