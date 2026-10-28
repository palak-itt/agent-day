import openai, json
from labs.w03_schema import TicketInsight, ActionItem
import os
import dotenv
dotenv.load_dotenv()
client = openai.OpenAI()
model = os.getenv("OPENAI_MODEL")

resp = client.chat.completions.create(model=model,
                                      tools = [{
                                          "type": "function",
                                          "function": {
                                              "name": "record_ticket",
                                              "description": "Record a ticket with the given details",
                                              "parameters": TicketInsight.model_json_schema()
                                              
                                          }
                                      }],
                                      tool_choice = {"type": "function", "function": {"name": "record_ticket"}},
                                      reasoning_effort="none",
                                      messages = [{"role": "user", "content": "Login page 500s since this morning, we're losing sales! - maria@acme.io"}],
)

tool_call = resp.choices[0].message.tool_calls[0]

# Arguments are returned as a JSON string
data = json.loads(tool_call.function.arguments)
print(data)

# Validate using Pydantic
ticket = TicketInsight.model_validate(data)
print(ticket)