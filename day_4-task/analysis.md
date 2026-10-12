# Day 4 – Agentic AI: Foundations and Open-Source Practice

## 1. Introduction and Scenario

The objective of this task is to understand how model size, quantization, context length, memory requirements, and licensing affect the selection of a language model for a practical application.

My scenario is running a local language model on a computer with 8 GB of available memory. The model should be suitable for learning and experimenting with AI applications while avoiding excessive memory usage. I use Ollama to run models locally and Python scripts to estimate their memory requirements.

The main goal is to select a model that fits the available hardware, provides acceptable performance, and has a licence compatible with the intended use.

## 2. Important Concepts

### 2.1 Model Weights

Model weights are the numerical values learned during the training of a language model. They store the information the model uses to generate responses.

Larger models generally require more memory to store their weights. For example, a model with billions of parameters requires more memory than a smaller model when both use the same numerical precision.

Ignoring weight memory can cause a model to exceed the available memory, resulting in performance problems or failure to load.

However, weight size alone does not represent the complete memory requirement because runtime overhead and the KV cache also consume memory.

### 2.2 Quantization

Quantization reduces the number of bits used to represent model weights. It can reduce storage requirements and make models easier to run on computers with limited memory.

In this experiment, I compare Q4_K_M, Q5_K_M, Q8_0, and FP16 configurations. Lower-bit quantization generally requires less memory, while higher precision retains more numerical detail.

Quantization is useful when selecting a model for limited hardware. However, reducing precision can affect response quality, depending on the model and task.

Therefore, the best quantization method should balance memory usage, response quality, and the requirements of the intended application.

### 2.3 KV Cache and Context Length

The KV cache stores intermediate key and value information used by the model while processing a conversation. It helps the model avoid repeating some calculations for previously processed tokens.

Context length determines how many tokens the model can consider within its working context. Increasing context length generally increases KV cache memory usage.

In my experiment, the context lengths are 1,024, 2,048, 4,096, and 8,192 tokens. The results show that the estimated KV cache grows as the context length increases.

A longer context is useful when processing lengthy documents or conversations. However, it requires more memory. Choosing an unnecessarily large context can waste resources, while a context that is too small may not support the intended task.

### 2.4 Model Card

A model card is documentation that describes a model, including its intended uses, limitations, training information, evaluation results, and other relevant details.

Before selecting a model, I should read its official model card to understand its capabilities and limitations. The model card may also provide information about the licence and whether the model supports features such as tool calling.

Ignoring model documentation can lead to selecting a model that is unsuitable for the task or misunderstanding its restrictions.

A model card is useful, but its claims should be interpreted in the context of the intended application. Actual performance should also be tested.

### 2.5 Open-Weight and Open-Source Licensing

Open-weight models make their trained weights available for use under the conditions specified by their licences. However, making model weights available does not automatically mean that the model is fully open-source.

Different models may have different conditions for personal use, research, redistribution, and commercial applications.

Before using a model in a project, I should verify the exact licence and any additional terms from the official model documentation.

Ignoring licence conditions can create legal or compliance problems, especially when distributing an application or using a model commercially.

## 3. Memory Estimation Method

I created a Python script named `memory_estimator.py` to estimate the memory requirements of different model configurations.

The script estimates memory using three main components:

1. Model weight memory.
2. KV cache memory.
3. Runtime overhead.

The estimated total is calculated by adding these components together.

For model weights, the number of parameters is multiplied by the assumed number of bytes per parameter. KV cache memory is estimated using the number of layers, KV heads, head dimension, context length, and assumed cache precision.

The available memory budget is set to 8 GB, with 0.8 GB reserved as runtime overhead in the simplified calculation.

The script compares the estimated total with the available memory and reports whether each configuration fits within the assumed budget.

These calculations provide a useful first estimate, but they are not exact measurements of real hardware usage. Actual memory consumption depends on the model implementation, quantization format, runtime, GPU or CPU allocation, and other system processes.

## 4. Context Length and Quantization Experiment

I created another Python script named `context_quantization_experiment.py` to study how context length and quantization affect estimated memory usage.

### 4.1 Context Length Experiment

In the first experiment, I fixed the model configuration and quantization at Q4_K_M and changed the context length from 1,024 to 8,192 tokens.

The results show that the estimated model weight memory remains constant because the model and quantization format do not change. However, the KV cache memory increases as the context length increases.

For the Llama 3.2 3B configuration used in the script, the estimated KV cache increases from approximately 0.117 GB at 1,024 tokens to 0.940 GB at 8,192 tokens.

All four tested context lengths fit within the simplified 8 GB memory budget under the assumptions used in the script.

This demonstrates that longer context lengths require additional memory even when the model weights remain unchanged.

### 4.2 Quantization Experiment

In the second experiment, I fixed the context length at 4,096 tokens and compared Q4_K_M, Q5_K_M, Q8_0, and FP16.

The results show that estimated weight memory increases as the assumed bytes per parameter increase. The KV cache remains unchanged in this experiment because the script keeps its precision fixed.

Among the tested configurations, Q4_K_M has the lowest estimated memory requirement, while FP16 has the highest.

The estimated total memory for FP16 is approximately 7.690 GB, which is close to the assumed 8 GB budget. This leaves very little room for additional memory consumption beyond the assumptions in the calculation.

Therefore, Q4_K_M is a practical starting point for limited-memory systems, although the final choice should also consider output quality and actual runtime behaviour.

## 5. Local Model Reality Check Using Ollama

I installed and tested the Qwen2.5 1.5B model using Ollama. The installed model is listed as `qwen2.5:1.5b`.

The `ollama list` command reported a model size of approximately 986 MB. When the model was running, the `ollama ps` command reported a size of approximately 1.2 GB.

The running model was reported as using 100% GPU processing, with a context length of 4,096 tokens and the `llamacpp` runner.

These observations show that the model can run locally in the tested environment. They also demonstrate that the size shown for an installed model and the size reported while it is running are not necessarily identical.

The values reported by Ollama should be interpreted according to what each command measures. In particular, the runtime size should not automatically be treated as the complete memory usage of the GPU or the entire system.

The Python estimator and Ollama measurements may differ because the estimator uses simplified assumptions, while actual execution depends on the model file, runtime implementation, memory allocation, and processing hardware.

A fair comparison requires estimating the same model with appropriate architecture details and then comparing the estimate with the observed runtime behaviour.

## 6. Model Selection and Suitability

For my current learning scenario, I would prioritise a model that fits within the available memory, runs reliably through Ollama, and supports experimentation with local AI applications.

Qwen2.5 1.5B is a useful starting point because I have already installed and tested it in my environment. Its observed runtime information provides a practical baseline for further experiments.

However, a smaller model may not perform as well as a larger model on complex reasoning, lengthy instructions, or advanced tool-use tasks. Model selection should therefore consider both hardware requirements and task performance.

Before choosing a model for a real application, I should compare its capabilities, official licence, context support, and available quantized versions. If the application requires commercial use, I must verify the licence terms rather than assuming that local availability means unrestricted permission.

A larger model could become a better choice if more memory becomes available or if the task requires stronger reasoning. A smaller or more heavily quantized model may be preferable when memory limitations and fast local execution are the main priorities.

## 7. Limitations of the Experiment

This experiment uses simplified memory calculations. The estimated results depend on the parameter counts, architecture details, quantization assumptions, KV cache precision, and runtime overhead entered into the Python scripts.

The assumed 8 GB budget and 0.8 GB runtime overhead are planning values, not guarantees of actual available GPU memory.

The experiments also focus on estimated memory rather than measuring response quality, inference speed, power consumption, or accuracy on a specific task.

Ollama's reported model sizes provide useful observations, but they do not by themselves establish the complete memory footprint of every hardware component.

To improve the experiment, I would verify the architecture details of every model from official documentation, record the exact model version and quantization, measure memory usage during inference, and test representative prompts.

I would also check official model cards and Ollama library pages for licensing information and feature support before making a final recommendation.

## 8. Conclusion

This experiment demonstrates that selecting a local language model requires more than checking its parameter count or download size.

Model weights determine an important part of memory usage, quantization changes the weight memory requirement, and context length affects KV cache memory. Runtime overhead must also be considered when estimating whether a model will fit within a hardware budget.

The experiment with Ollama provides a practical way to compare theoretical estimates with a real model running locally. Differences between estimated and observed values highlight the limitations of simplified calculations.

Finally, a suitable model must meet both technical and licensing requirements. By evaluating memory, quantization, context length, actual runtime behaviour, model documentation, and licence conditions together, I can make a more informed choice for local AI development.
