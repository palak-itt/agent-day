import re, json
from collections import Counter
from app.clients import ask_gpt, ask_local

CASES = [
    ("A shop sells pens at 12 rupees each. Riya buys 7 pens and pays with a 100 rupee note. How much change does she get?", "16"),
    ("A train leaves at 9:40 and arrives at 13:15 the same day. How many minutes is the journey?", "215"),
    ("There are 3 boxes, each holds 4 bags, each bag holds 5 apples. I eat 7 apples. How many are left?", "53"),
    ("Tom is twice as old as Sam. In 6 years the sum of their ages will be 48. How old is Tom now?", "24"),
    ("A tank fills at 8 litres/min but leaks 3 litres/min. How many minutes to fill 90 litres?", "18"),
    ("What is 17% of 2400?", "408"),
    ("Alice is taller than Bob. Carol is shorter than Bob. Dan is taller than Alice. Who is the second tallest?", "alice"),
    ("How many times does the letter 'e' appear in the word 'excellence'?", "4"),
]

ZERO = "Answer with ONLY the final answer, in the form 'ANSWER: <value>'.No explaination.\n\n{q}"
COT = "Think step by step, then finish with a line in the form 'ANSWER: <value>'.\n\n{q}"

def parse(text):
    m= re.findall(f"ANSWER:\s*(.+)", text, flags=re.I)
    return m[-1].strip().strip(".").lower() if m else ""

def run(fn, template, **kw):
    results = []
    for q, gold in CASES:
        text = fn(template.format(q=q), **kw)[0]
        print(text)
        results.append(parse(text) == gold)
    return results

gpt = lambda p, **kw: ask_gpt(p, max_completion_tokens=500, **kw)
local = lambda p, **kw: ask_local(p, **kw)

# table ={}
# for model_name, fn, temp in [("gpt", gpt, 1), ("local-3b", local, 0)]:
#     print(f"Running tests for {model_name} zero-shot with temperature {temp}")
#     table[(model_name, "zero-shot")] = run(fn, ZERO, temperature=temp)
#     print(f"Running tests for {model_name} cot with temperature {temp}")
#     table[(model_name, "cot")] = run(fn, COT, temperature=temp)


# print("case | " + " | ".join(f"{m}/{s}" for m, s in table))
# for i in range(len(CASES)):
#     print(f"{i+1}    | " + " | ".join("PASS" if table[k][i] else "FAIL" for k in table))
# print("score:", {f"{m}/{s}": f"{sum(v)}/{len(v)}" for (m, s), v in table.items()})

def self_consistent(q, n=5):
    answers = []
    for _ in range(n):
        text = ask_local(COT.format(q=q), temperature=0.8)[0]
        answers.append(parse(text))
    a, votes = Counter(answers), Counter(answers).most_common(1)[0]
    return a, votes, answers

print(self_consistent(CASES[1][0]))