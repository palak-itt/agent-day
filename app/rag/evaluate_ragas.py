
from dotenv import load_dotenv
import asyncio
import inspect
import json
import os
from pathlib import Path

from openai import AsyncOpenAI
from google import genai

from ragas.llms import llm_factory
from ragas.embeddings import GoogleEmbeddings

from ragas.metrics.collections import (
    Faithfulness,
    AnswerRelevancy,
    ContextPrecision,
    ContextRecall,
)

from .answer import rag_answer

load_dotenv()


# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

EVAL_FILE = Path("data/eval/eval_set.json")
OUTPUT_DIR = Path("outputs")

K = 5

LLM_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-6-luna"
)

EMBEDDING_MODEL = "gemini-embedding-001"

STRATEGY = "recursive"

# Incremental output file
OUTPUT_FILE = (
    OUTPUT_DIR / f"ragas_results_{STRATEGY}.json"
)


# --------------------------------------------------
# 2. OPENAI GPT JUDGE
# --------------------------------------------------

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "OPENAI_API_KEY not found. Check your .env file."
    )

base_url = os.getenv("OPENAI_BASE_URL")

client = AsyncOpenAI(
    api_key=api_key,
    base_url=base_url if base_url else None,
)

judge_llm = llm_factory(
    model=LLM_MODEL,
    provider="openai",
    client=client,
)


# --------------------------------------------------
# 3. VERIFY JUDGE LLM
# --------------------------------------------------

print("\n========== JUDGE LLM VERIFICATION ==========")

print("Judge model:", LLM_MODEL)
print("Judge LLM:", type(judge_llm))

if isinstance(client, AsyncOpenAI):

    print("Async client verification: PASSED")

else:

    raise TypeError(
        "Expected an AsyncOpenAI client."
    )

if hasattr(judge_llm, "agenerate"):

    print("Async generation method: AVAILABLE")

else:

    raise RuntimeError(
        "RAGAS async generation is unavailable."
    )

print("============================================\n")


# --------------------------------------------------
# 4. GOOGLE EMBEDDINGS
# --------------------------------------------------

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError(
        "GEMINI_API_KEY is required for Google embeddings."
    )

embedding_client = genai.Client(
    api_key=gemini_api_key
)

judge_embeddings = GoogleEmbeddings(
    model=EMBEDDING_MODEL,
    client=embedding_client,
)


# --------------------------------------------------
# 5. RAGAS METRICS
# --------------------------------------------------

faithfulness_metric = Faithfulness(
    llm=judge_llm
)

relevance_metric = AnswerRelevancy(
    llm=judge_llm,
    embeddings=judge_embeddings,
)

precision_metric = ContextPrecision(
    llm=judge_llm
)

recall_metric = ContextRecall(
    llm=judge_llm
)


# --------------------------------------------------
# 6. EXTRACT RAG RESULTS
# --------------------------------------------------

def extract_result(result):

    if isinstance(result, dict):

        answer = result.get(
            "answer",
            result.get("response")
        )

        hits = result.get(
            "hits",
            result.get(
                "retrieved_contexts",
                result.get("contexts", [])
            )
        )

    elif isinstance(result, tuple) and len(result) == 2:

        answer, hits = result

    else:

        raise ValueError(
            "Unexpected rag_answer() return format. "
            "Expected dict or (answer, hits) tuple."
        )

    if answer is None:
        raise ValueError("RAG answer is missing.")

    if isinstance(hits, str):
        hits = [hits]

    if hits is None:
        hits = []

    contexts = []

    for hit in hits:

        if isinstance(hit, str):

            contexts.append(hit)

        elif isinstance(hit, dict):

            text = hit.get(
                "text",
                hit.get("document", "")
            )

            if text:
                contexts.append(text)

        else:

            raise TypeError(
                f"Unsupported retrieved hit type: {type(hit)}"
            )

    if not contexts:
        print("WARNING: No retrieved contexts extracted.")

    return str(answer), contexts


# --------------------------------------------------
# 7. LOAD EVALUATION DATA
# --------------------------------------------------

def load_eval_data():

    if not EVAL_FILE.exists():

        raise FileNotFoundError(
            f"Evaluation file not found: {EVAL_FILE}"
        )

    with open(EVAL_FILE, encoding="utf-8") as f:

        data = json.load(f)

    if not isinstance(data, list):

        raise ValueError(
            "Evaluation dataset must be a JSON list."
        )

    return data


# --------------------------------------------------
# 8. INCREMENTAL SAVE / RESUME
# --------------------------------------------------

def save_results(rows, total_questions):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Keep rows in original evaluation order
    ordered_rows = [
        rows[i]
        for i in sorted(rows)
    ]

    valid = [
        row for row in ordered_rows
        if row.get("scores")
    ]

    metric_names = [
        "faithfulness",
        "answer_relevance",
        "context_precision",
        "context_recall",
    ]

    summary = {}

    for metric in metric_names:

        values = [
            row["scores"][metric]
            for row in ordered_rows
            if metric in row.get("scores", {})
        ]

        summary[metric] = (
            sum(values) / len(values)
            if values else None
        )

    output = {
        "strategy": STRATEGY,
        "k": K,
        "judge_model": LLM_MODEL,
        "embedding_model": EMBEDDING_MODEL,
        "total_questions": total_questions,
        "generated_answers": sum(
            1 for row in ordered_rows
            if "response" in row
        ),
        "evaluated_questions": len(valid),
        "summary": summary,
        "rows": ordered_rows,
    }

    # Write to temporary file first
    temp_file = OUTPUT_FILE.with_suffix(".tmp")

    with open(temp_file, "w", encoding="utf-8") as f:

        json.dump(
            output,
            f,
            indent=2,
            ensure_ascii=False,
        )

        f.flush()
        os.fsync(f.fileno())

    # Replace previous output atomically
    os.replace(
        temp_file,
        OUTPUT_FILE,
    )


def load_previous_results():

    if not OUTPUT_FILE.exists():
        return {}

    print("\nExisting results found.")
    print("Loading previous progress for resume...")

    with open(OUTPUT_FILE, encoding="utf-8") as f:

        previous = json.load(f)

    if previous.get("strategy") != STRATEGY:
        raise ValueError(
            "Existing results belong to another strategy."
        )

    # Map rows using their question index
    saved_rows = {}

    for row in previous.get("rows", []):

        index = row.get("question_index")

        if index is not None:
            saved_rows[index] = row

    print(
        f"Loaded {len(saved_rows)} previously processed rows."
    )

    return saved_rows


# --------------------------------------------------
# 9. GENERATE ONE ANSWER
# --------------------------------------------------

def generate_one(item, index):

    print(
        f"\nGenerating answer for question {index + 1}"
    )

    print("Question:", item["q"])

    result = rag_answer(
        item["q"],
        strategy=STRATEGY,
    )

    if inspect.isawaitable(result):

        result = asyncio.run(result)

    answer, contexts = extract_result(result)

    print("\nGenerated answer:")
    print(answer)

    print("\nRetrieved contexts:", len(contexts))

    return answer, contexts


# --------------------------------------------------
# 10. SCORE ONE METRIC AT A TIME
# --------------------------------------------------

def calculate_metric(metric_name, row):

    q = row["q"]
    response = row["response"]
    contexts = row["retrieved_contexts"]
    reference = row["reference"]

    if metric_name == "faithfulness":

        result = faithfulness_metric.score(
            user_input=q,
            response=response,
            retrieved_contexts=contexts,
        )

    elif metric_name == "answer_relevance":

        result = relevance_metric.score(
            user_input=q,
            response=response,
        )

    elif metric_name == "context_precision":

        result = precision_metric.score(
            user_input=q,
            retrieved_contexts=contexts,
            reference=reference,
        )

    elif metric_name == "context_recall":

        result = recall_metric.score(
            user_input=q,
            retrieved_contexts=contexts,
            reference=reference,
        )

    else:

        raise ValueError(
            f"Unknown metric: {metric_name}"
        )

    return float(result.value)


# --------------------------------------------------
# 11. RUN ALL QUESTIONS
# --------------------------------------------------

def run():

    eval_data = load_eval_data()

    # Load previous results if restarting
    results = load_previous_results()

    metric_names = [
        "faithfulness",
        "answer_relevance",
        "context_precision",
        "context_recall",
    ]

    print("\n============================================")
    print("RAGAS INCREMENTAL EVALUATION")
    print("============================================")

    print("Strategy:", STRATEGY)
    print("Total questions:", len(eval_data))
    print("Judge:", LLM_MODEL)
    print("Metrics:", len(metric_names))
    print("============================================")

    # Process questions one by one

    for index, item in enumerate(eval_data):

        question_number = index + 1

        print("\n")
        print("#" * 55)
        print(
            f"QUESTION {question_number}/{len(eval_data)}"
        )
        print("#" * 55)

        # Get existing row or create a new one
        row = results.get(
            index,
            {
                "question_index": index,
                "q": item["q"],
                "reference": item.get("gt", ""),
                "source": item.get("source", ""),
                "trap": item.get("trap", False),
                "scores": {},
                "metric_errors": {},
            }
        )

        # ------------------------------------------
        # A. GENERATE ANSWER
        # ------------------------------------------

        if "response" not in row:

            try:

                answer, contexts = generate_one(
                    item,
                    index,
                )

                row["response"] = answer
                row["retrieved_contexts"] = contexts

                # Save answer immediately
                results[index] = row

                save_results(
                    results,
                    len(eval_data),
                )

                print("\nANSWER SAVED SUCCESSFULLY.")

            except Exception as e:

                row["generation_error"] = str(e)

                results[index] = row

                save_results(
                    results,
                    len(eval_data),
                )

                print("\nANSWER GENERATION FAILED:")
                print(repr(e))

                print("Moving to next question.")

                continue

        else:

            print("Answer already generated. Skipping generation.")

        # ------------------------------------------
        # B. SKIP TRAP / NO REFERENCE QUESTIONS
        # ------------------------------------------

        if row["trap"] or not row["reference"]:

            print(
                "\nSKIPPING SCORING: Trap/no-reference question."
            )

            row["skipped"] = True
            row["skip_reason"] = "Trap/no-reference row"

            results[index] = row

            save_results(
                results,
                len(eval_data),
            )

            continue

        # ------------------------------------------
        # C. CALCULATE METRICS ONE BY ONE
        # ------------------------------------------

        for metric_name in metric_names:

            # Skip already completed metrics
            if metric_name in row["scores"]:

                print(
                    f"\n{metric_name}: Already completed. Skipping."
                )

                continue

            print("\n" + "-" * 45)
            print(f"Calculating: {metric_name}")
            print("-" * 45)

            try:

                score = calculate_metric(
                    metric_name,
                    row,
                )

                # Save immediately after successful metric
                row["scores"][metric_name] = score

                # Clear previous error if retry succeeded
                row.get("metric_errors", {}).pop(
                    metric_name,
                    None,
                )

                results[index] = row

                save_results(
                    results,
                    len(eval_data),
                )

                # Print immediately
                print(
                    f"\nSUCCESS: {metric_name} = {score:.4f}"
                )

                print("RESULT SAVED TO JSON.")

            except Exception as e:

                error_message = str(e)

                row.setdefault(
                    "metric_errors",
                    {}
                )[metric_name] = error_message

                results[index] = row

                save_results(
                    results,
                    len(eval_data),
                )

                print(
                    f"\nFAILED: {metric_name}"
                )

                print("Error:", repr(e))

                print(
                    "Previous successful scores are preserved."
                )

                # Continue with the next metric
                continue

        # ------------------------------------------
        # D. QUESTION SUMMARY
        # ------------------------------------------

        print("\n" + "=" * 45)
        print(f"QUESTION {question_number} SUMMARY")
        print("=" * 45)

        for metric_name in metric_names:

            if metric_name in row["scores"]:

                print(
                    f"{metric_name}: "
                    f"{row['scores'][metric_name]:.4f}"
                )

            else:

                print(
                    f"{metric_name}: NOT COMPLETED"
                )

        print("=" * 45)

    # --------------------------------------------------
    # 12. FINAL SUMMARY
    # --------------------------------------------------

    save_results(
        results,
        len(eval_data),
    )

    print("\n\n========== FINAL RAGAS SUMMARY ==========")

    for metric_name in metric_names:

        values = [
            row["scores"][metric_name]
            for row in results.values()
            if metric_name in row.get("scores", {})
        ]

        if values:

            average = sum(values) / len(values)

            print(
                f"{metric_name}: {average:.4f} "
                f"({len(values)} successful scores)"
            )

        else:

            print(f"{metric_name}: No scores available.")

    print("\nTotal questions:", len(eval_data))

    print(
        "Generated answers:",
        sum(
            1 for row in results.values()
            if "response" in row
        )
    )

    print(
        "Questions with scores:",
        sum(
            1 for row in results.values()
            if row.get("scores")
        )
    )

    print("\nResults saved to:", OUTPUT_FILE)


# --------------------------------------------------
# 13. ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":

    run()
