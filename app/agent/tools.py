import os
from langchain_core.tools import tool
from app.rag.hybrid import hybrid_search

def make_tools(allowed_access=("public",)):
    @tool
    def search_docs(query: str) -> str:
        """Search the documentation set. Returns passages tagged [file#chunk]. Use for ANY factual questions about the docs"""
        hits = hybrid_search(query, k=4, allowed_access=allowed_access)
        if not hits:
            return "no results"
        return "\n\n".join(f"[{h['meta']['source']}#{h['meta']['chunk']}] {h['text']}" for h in hits)

    @tool
    def calculator(expression: str) -> str:
        """Evaluates an arithmetic expression such as '(12*7)/3'. Digits and + - * / () . only."""
        if not set(expression) <= set("0123456789+-*/(). "):
            return "TOOL ERROR: only digits and + - * / ( ) . are allowed"
        return str(eval(expression, {"__builtins__": {}}, {}))

    @tool
    def get_account_status(account_id: str) -> str:
        """Look up the billing status of a customer by account id"""
        if os.getenv("BREAK_TOOLS") == "1":
            raise ConnectionError("billing service unreachable")
        return f"account: {account_id}\n Status=Active\t plan=pro"

    return [search_docs, calculator, get_account_status]


