import json, os, time
from langchain_core.messages import SystemMessage, ToolMessage, AIMessage, HumanMessage
from langgraph.graph import StateGraph, MessagesState, START, END

SYSTEM = """You are DocOps, an assistant for a documentation set.
- For factual questions about the docs, call search_docs and answer ONLY from what it returns. Cite sources as [file#chunk].
- Use calculator for arithmetic; never do arithmetic in your head.
- If a tool returns an error or no results, say so plainly. NEVER invent a result.
- If the docs do not contain the answer, say you don't know."""

def text_of(msg):
    c=msg.content
    return c if isinstance(c, str) else " ".join(b.get("text", "") for b in c if isinstance(c, dict))

def build_agent(llm, tools, checkpointer=None, system=SYSTEM):
    llm_t = llm.bind_tools(tools)
    by_name = {t.name: t for t in tools}

    async def agent_node(state: MessagesState):
        reply = await llm_t.ainvoke([SystemMessage(content=SYSTEM)] + state["messages"])
        return {"messages": [reply]}

    async def tool_node(state: MessagesState):
        out = []
        for call in state['messages'][-1].tool_calls:
            try:
                res = await by_name[call["name"]].ainvoke(call["args"])
            except Exception as e:
                res = f"TOOL_ERROR: {type(e).__name__}: {e}"
            out.append(ToolMessage(content=str(res), tool_call_id=call["id"], name=call["name"]))
        return {"messages": out}

    def route(state: MessagesState):
        return "tools" if state["messages"][-1].tool_calls else "end"

    g=StateGraph(MessagesState)
    g.add_node("agent", agent_node)
    g.add_node("tools", tool_node)
    g.add_edge(START, "agent")
    g.add_conditional_edges("agent", route, {"tools": "tools", "end": END})
    g.add_edge("tools", "agent")
    return g.compile(checkpointer=checkpointer)

def show(m):
    if isinstance(m, AIMessage):
        t=text_of(m)
        if t:
            print("  THOUGHT/ANSWER:", t[:400])
        for c in m.tool_calls:
            print(f"  ACTION        → {c['name']}({json.dumps(c['args'])[:200]})")
    elif isinstance(m, ToolMessage):
        print(f"  OBSERVATION   ← {m.content[:250]!r}")

async def run(graph, question, thread_id="t1", extra_config=None, trace_dir="traces"):
    config = {"configurable": {"thread_id": thread_id, "recursion_limit": 25, **(extra_config or {})}}
    os.makedirs(trace_dir, exist_ok=True)
    final, t0 = "", time.time()
    print(f"\nQ: {question}")
    async for step in graph.astream({"messages": [HumanMessage(content=question)]}, config, stream_mode = "updates"):
        for node, upd in step.items():
            if node == "__interrupt__":
                print(" INTERRUPT : ", upd)
                continue
            for m in upd.get("messages", []):
                show(m)
                with open(f"{trace_dir}/{thread_id}.jsonl", "a") as f:
                    f.write(json.dumps({"t": round(time.time() - t0, 2), "node": node,
                                        "type": m.type, "content": str(m.content)[:2000],
                                        "tool_calls": getattr(m, "tool_calls", None)}) + "\n")
                if isinstance(m, AIMessage) and not m.tool_calls:
                    final = text_of(m)
    return final





