import asyncio, os
from app.clients import chat_model
from app.agent.tools import make_tools
from app.agent.graph import build_agent, run

async def main():
    agent = build_agent(chat_model(), make_tools())
    await run(agent, "What is 48213 * 3917?", "a1")                                  # calculator only
    await run(agent, "How do custom validators work in these docs?", "a2")           # search
    await run(agent, "Hello!", "a3")                                                  # no tools at all
    await run(agent, "Search the docs for the validator concept, then tell me how many characters 'validator' has, times 3.", "a4") 
    await run(agent, "What is 48213 * 3917?", "a1")                                  # calculator only
    await run(agent, "How do custom validators work in these docs?", "a2")           # search
    await run(agent, "Hello!", "a3")                                                  # no tools at all
    await run(agent, "Search the docs for the validator concept, then tell me how many characters 'validator' has, times 3.", "a4") 
asyncio.run(main())