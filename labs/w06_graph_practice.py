from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
import operator
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver

class RAGStateReducer(TypedDict):
    question: str
    docuemnts: Annotated[list, operator.add]
    # Annotated tells LangGraph that this field has additional metadata.
    # operator.add is our reducer.
    # For lists, operator.add concatenates the lists.

class RAGState(TypedDict):
    question: str
    documents: list
    answer: str

# Each node recieves the state and return updated to it
# We can have nodes for:
# - Retrieval
# - Query rewriting
# - Document grading
# - LLM generation
# - Tool execution
def rag_answer(question):
    hits = hybrid_search(question)
    context = format_context(hits)
    answer = ask_gpt(question, context)
    return answer
# There is no choice, it always searches
# Fixed pipeline, every question follows the same path

def retrieve(state):
    hits = hybrid_search(question["state"])
    return {"documents": hits}

def generate(state):
    answer = ask_gpt(state["question"], state["documents"])
    return {"answer": answer}

# nodes are simply functions.
# "langgraph internally handles state updates"

def check_relevance(state):
    if state["documents"]:
        return "generate"
    return "retrieved"





builder = StateGraph(RAGState)

# register nodes
builder.add_node("retrieve", retrieve)
builder.add_node("generate", generate)

# define execution order
builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "generate")
builder.add_conditional_edges("retrieve", check_relevance, {"generate": "generate", "rewrite": "rewrite"})
builder.add_edge("generate", END)

graph = builder.compile(checkpointer=checkpointer)

result = graph.invoke({
    "question": "What is RAG",
    "documents": [],
    "answer": ""
})
print(result["answer"])