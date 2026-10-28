# from app.clients import ask_gpt, ask_local
import random
import os
from dotenv import load_dotenv
import openai

load_dotenv()

def create_ticket(category, priority):
    return {"ID": random.randint(1000, 9999), "category": category, "priority": priority}

TOOLS = [
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
for _ in range(1):
    resp_t = client.chat.completions.create(
    model=model,
    messages=message,
    tools=TOOLS,
    reasoning_effort="none"
    )
    print(resp_t)
    # if resp_t.choices[0].finish_reason == "tool_calls":
    #     tool_call = resp_t.choices[0].message.tool_calls[0]
    


# text_t, _, _ = ask_gpt("""Extract JSON with keys summary, category, priority from: "Login page 500s since this morning, we are losing sales!" """, tools =TOOLS)
# print(text_t)
