import torch

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM
)

MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"

print("Loading tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)

print("Tokenizer loaded.")

print("Loading AI model...")

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    dtype=torch.float32,
    low_cpu_mem_usage=True
)

model.eval()

torch.set_num_threads(10)

try:
    torch.set_num_interop_threads(2)
except RuntimeError:
    pass

print("AI model loaded successfully!")
print("Device: CPU")
print("CPU threads:", torch.get_num_threads())