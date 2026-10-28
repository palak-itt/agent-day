from app.clients import ask_gpt

ticket = "I was charged twice for my March invoice and nobody replies to my emails!!"

zero = "Classify this ticket as one of: billing, bug, feature_request, other.\n Ticket:" + ticket
few = """Classify each support ticket as one of: billing, bug, feature_request, other.
Ticket: The export button crashes the app. -> bug
Ticket: Please add dark mode. -> feature_request
Ticket: Where can I update my card? -> billing
Ticket: """ + ticket + " ->"

for name, p in [("zero-shot", zero), ("few-shot", few)]:
    out, usage, _ = ask_gpt(p, max_completion_tokens=40, temperature=1)
    open(f"outputs/w02_roles_{name}.md", "a").write(out + "\n" + str(usage) + "\n" + "---" + "\n")
    print(name, "|", out.strip(), "|", usage)

#system role: persistnet behavior

out, usage, _ = ask_gpt(ticket, system="you are a terse support triager, Reply with only: CATEGORY | URGENCY(1-5).", max_completion_tokens=160, temperature=1)
print("system role |", out.strip(), "|", usage)
open(f"outputs/w02_roles_{name}.md", "a").write(out + "\n" + str(usage) + "\n" + "---" + "\n")
