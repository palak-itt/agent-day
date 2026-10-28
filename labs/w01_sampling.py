import tiktoken
from app.clients import ask_local, ask_gpt

PROMPT = "Write a one-sentence tagline for a coffee shop run by robots."
TEMPS= [0.0, 0.8, 1.5]

lines = ["| temp | run | output |", "|---|---|---|" ]

for T in TEMPS:
    for run in range(1,6):
        out, _, _ = ask_local(PROMPT, temperature=T, num_predict=40)
        # out, _, _ = ask_gpt(PROMPT, temperature=T, max_completion_tokens=40)

        lines.append(f"| {T} | {run} | {out.strip().replace(chr(10), ' ')} |")

open("outputs/w01_outputs_local.md", "w").write("\n".join(lines))
print("\n".join(lines))

# PART2: tokenize 3 prompts of different lengths
enc = tiktoken.get_encoding("cl100k_base")
prompts = {
    "short": "Hello!",
    "medium": "Explain what a Delta Lake transaction log is and why it matters.",
    "long":  "Explain what a Delta Lake transaction log is and why it matters. " * 20,
}

for name, p in prompts.items():
    n = len(enc.encode(p))
    print(f"{name:7s} chars={len(p):5d} tokens={n:4d} chars/token={len(p)/n:.2f}")