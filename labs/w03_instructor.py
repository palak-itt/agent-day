import openai, json, argparse, sys
import instructor
import os
from labs.w03_schema import TicketInsight, ActionItem
import dotenv
dotenv.load_dotenv()

model = os.getenv("OPENAI_MODEL")

client = instructor.from_provider(f"openai/{model}")

def analyse(text: str) -> TicketInsight:
    return client.create(
        response_model = TicketInsight,
        max_retries = 3,
        reasoning_effort = "none",
        messages = [
            {
                "role": "user",
                "content":  (
                    "Analyse the following text. Only state facts present in it.\n\n"
                    "<text>\n" + text + "\n</text>"
                )
            }
        ]
    )

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    args = ap.parse_args()
    # texts = [open(f).read() for f in args.files] or [sys.stdin.read()]

    import glob

    files = []
    for f in args.files:
        files.extend(glob.glob(f))

    texts = [open(f, encoding="utf-8").read() for f in files] or [sys.stdin.read()]
    for text in texts:
        res = analyse(text).model_dump_json(indent=2)
        open('outputs/w03_instructor.json', 'a', encoding="utf-8").write(res)
        print(res)
