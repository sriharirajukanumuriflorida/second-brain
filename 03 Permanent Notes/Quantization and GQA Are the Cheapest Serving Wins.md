# Quantization and GQA Are the Cheapest Serving Wins

Two levers cut LLM serving cost with little effort and small quality loss: **post-training quantization** (GPTQ/AWQ to INT4/INT8) halves-to-quarters weight memory and boosts throughput with no retraining; **GQA/MQA** shrink the KV cache by sharing K/V across query heads, which matters most at long context and large batch (where KV can exceed the weights). Combined with FlashAttention and continuous batching (vLLM), they routinely deliver multi-fold cost reductions.

Always validate the quantized model on your own eval set — 4-bit can hurt hard reasoning tasks.

> One-liner: **quantize the weights, GQA the KV cache** — the highest ROI efficiency moves before you touch the model itself.


Related: [[02 Literature Notes/LLM Engineering/LLM Efficiency]] · [[02 Literature Notes/LLM Engineering/Inference and Serving]]
