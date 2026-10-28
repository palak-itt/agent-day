import re
from app.clients import ask_gpt, ask_local

FACTS = {"capital of france": "Paris", "population of paris": "about 2.1 million"}

def search(q): return FACTS.get(q.lower().strip(), "no result")

def calc(expr):
    return str(eval(expr, {"__builtins__": {}}, {})) if set(expr) <= set("0123456789+-*/(). ") else "bad input"

SYSTEM = """ Answer by looping Thought/Action/Observation. Tools:
search[query] - look up a fact; calc[expression -arithmetic].
Format EXACTLY:
Thought: ...
Action: tool[input]
Then STOP and wait for Observation, When done write:
Thought: ...
Final Answer: ...
"""

question = "What is the population of the capital of France, doubled?"

transcript = f"Question: {question}\n"

for _ in range(6):
    # text,_,_ = ask_gpt(transcript, SYSTEM, temperature =1)
    text,_,_ = ask_local(transcript, SYSTEM, temperature =1, stop=["Observation:"])
    transcript += text + "\n"
    if "Final Answer:" in text:
        break
    m = re.search(r"Action:\s*(\w+)\[(.*)\]", text)
    obs = {"search": search, "calc": calc}.get(m.group(1), lambda x: "unknown tool")(m.group(2)) if m else "no action found"
    transcript += f"\n Observation: {obs} \n"
open("outputs/w02_react_local.md", "a").write(transcript)

print(transcript)