# LoRA Learns a Low Rank Delta Not a New Model

LoRA freezes the base matrix and learns `ΔW=(α/r)BA`. The adapter is the task-specific delta; the base remains shared. This slashes trainable parameters and optimizer state.

> One-liner: **LoRA fine-tunes the patch, not the foundation.**


Related: [[02 Literature Notes/LLM Engineering/LoRA QLoRA PEFT]]
