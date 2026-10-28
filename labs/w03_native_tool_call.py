# from app.clients import ask_gpt, ask_local
import json
import random
import os
from dotenv import load_dotenv
import openai

load_dotenv()

def create_ticket(category, priority):
    return {"ID": random.randint(1000, 9999), "category": category, "priority": priority}

TOOLS = {
    "create_ticket": create_ticket
}
tool_specs = [
    {"type": "function",
     "function": {
         "name": "create_ticket",
         "description": "Classify a support ticket",
         "parameters": {
             "type": "object",
             "properties":{
                 "category": {
                     "type": "string",
                     "enum": ["incident", "question", "feature_request", "other"]
                 },
                 "priority": {
                     "type": "string",
                     "enum": ["low", "medium", "high", "critical"]
                 }
                
             },
             "required": ["category", "priority"],
             "additionalProperties": False
         },
         "strict": True
     }
     }
]
model = os.getenv("OPENAI_MODEL", "gpt-6-luna")
client = openai.OpenAI()
# resp = client.chat.completions.create(
#     model=model,
#     messages=[
#         {
#             "role": "user",
#             "content": """Extract JSON with keys summary, category, priority from: "Login page 500s since this morning, we are losing sales!" """
#         }
#     ]
# )
# print(resp)
message = [
        {
            "role": "user",
            "content": """Extract JSON with keys summary, category, priority from: "Login page 500s since this morning, we are losing sales!" """
        }
    ]
for _ in range(3):
    resp_t = client.chat.completions.create(
    model=model,
    messages=message,
    tools=tool_specs,
    reasoning_effort="none"
    )
    print(resp_t)
    print()
    message.append(resp_t.choices[0].message)
    if not resp_t.choices[0].message.tool_calls:
        print("FINAL: ", resp_t.choices[0].message.content)
        break
    if resp_t.choices[0].finish_reason == "tool_calls":
        tool_call = resp_t.choices[0].message.tool_calls[0]
        res = TOOLS[tool_call.function.name](**json.loads(tool_call.function.arguments))
        print(res)
        print("Tool call executed successfully.")
        message.append({"role": "tool", "name": tool_call.function.name, "tool_call_id": tool_call.id, "content": json.dumps(res)})

    


# text_t, _, _ = ask_gpt("""Extract JSON with keys summary, category, priority from: "Login page 500s since this morning, we are losing sales!" """, tools =TOOLS)
# print(text_t)
