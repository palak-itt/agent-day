import json, sys
import instructor
from pydantic import BaseModel, Field
from app.clients import OPENAI_MODEL
from .answer import rag_answer

judge = instructor.from_provider(f"openai/{OPENAI_MODEL}")

class Verdict(BaseModel):
    faithful: bool = Field(description="Every factual claim in the answer is supported by the context")
    correct: bool = Field(description= "The answer agrees witht he ground truth")
    reason: str

class TrapVerdict(BaseModel):
    abstained: bool = Field(
        description="True if the answer clearly states that the provided documents do not contain sufficient information. False if it provides an unsupported answer."
    )
    reason: str

def judge_one(q, answer, gt, ctx):
    return judge.create(response_model=Verdict, max_retries=2, reasoning_effort="none", max_completion_tokens=300, messages=[{"role":"user", "content": f"Question: {q}\n Ground truth: {gt}\n Context: \n {ctx}\n\nAnswer to grade: \n{answer}"}])

def judge_trap(q, answer, ctx):
    return judge.create(
        response_model=TrapVerdict,
        max_retries=2,
        reasoning_effort="none",
        max_completion_tokens=200,
        messages=[{
            "role": "user",
            "content": f"""
            Evaluate whether the RAG system correctly handled this question.

            The question is labelled as unanswerable in the evaluation dataset.
            Your task is to evaluate ONLY the generated answer.

            Set abstained=True if:
            - The answer clearly says the documents lack sufficient information.
            - It does not present an unsupported explanation as fact.

            Set abstained=False if:
            - It gives an unsupported answer.
            - It guesses or invents a specific explanation.
            - It presents speculation as established fact.

            Question: {q}
            Retrieved context: {ctx}
            Generated answer: {answer}
            """
        }]
    )


def run(strategy="recursive", k=5):
    items = json.load(open("data/eval/eval_set.json"))
    rows= []
    for it in items:
        r = rag_answer(it["q"], k=k, strategy=strategy)
        # sources = [h["meta"]["source"] for h in r["hits"]]
        sources = [
            h["meta"]["source"].replace("\\", "/")
            for h in r["hits"]
        ]
        expected_source = it["source"].replace("\\", "/")

        row = dict(q=it["q"], trap=it["trap"], answer=r["answer"])
        if it["trap"]:
            # row["pass"] = "i don't know" in r["answer"].lower()
            ctx = "\n".join(h["text"] for h in r["hits"])
            v = judge_trap(it["q"], r["answer"], ctx)

            row["pass"] = v.abstained
            row["why"] = v.reason
        else:
            # row["hit"] = it["source"] in sources
            # rank = sources.index(it["source"]) + 1 if row["hit"] else None
            row["hit"] = expected_source in sources
            rank = sources.index(expected_source) + 1 if row["hit"] else None
            row["mrr"] = 1/rank if rank else 0.0
            v = judge_one(it["q"], r["answer"], it["gt"], "\n".join(h["text"] for h in r["hits"]))
            row.update(faithful=v.faithful, correct=v.correct, why=v.reason)
            row["failure"] = ("retrieval" if not row["hit"] else "generation" if not v.correct else None)
        rows.append(row)
    return rows

if __name__ == "__main__":
    rows = run(sys.argv[1] if len(sys.argv) > 1 else "recursive")
    q = [r for r in rows if not r["trap"]]; t = [r for r in rows if r["trap"]]
    print(f"hit@5     {sum(r['hit'] for r in q)}/{len(q)}")
    print(f"MRR       {sum(r['mrr'] for r in q)/len(q):.2f}")
    print(f"faithful  {sum(r['faithful'] for r in q)}/{len(q)}")
    print(f"correct   {sum(r['correct'] for r in q)}/{len(q)}")
    print(f"traps ok  {sum(r['pass'] for r in t)}/{len(t)}")
    for r in rows:
        if r.get("failure") or r.get("pass") is False:
            print("\nFAIL:", r["q"], "->", r.get("failure", "trap answered"), "|", r["answer"][:150])
    json.dump(rows, open("outputs/eval_rows_fixed.json", "a"), indent=2)