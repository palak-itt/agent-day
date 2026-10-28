import os
import time
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-5-5")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-6-luna")

def ask_claude(prompt, system=None, max_tokens=300, **kwargs):
    """Ask Claude a question using the Anthropic API.

    Args:
        prompt (str): The question or prompt to ask Claude.
        system (str, optional): System message to provide context.
        max_tokens (int, optional): Maximum number of tokens to generate.
        **kwargs: Additional keyword arguments for the API call.

    Returns:
        tuple: A tuple containing the following elements:
            - text (str): The generated response from Claude.
            - usage_dict (dict): A dictionary with input and output token usage.
            - latency_seconds (float): The time taken for the API call in seconds.
    """
    import anthropic
    client = anthropic.Anthropic() #reads ANTHROPIC API key from environment
    params = dict(
        model=ANTHROPIC_MODEL,
        max_tokens=max_tokens,
        messages = [{"role":"user", "content": prompt}],
        **kwargs,
    )
    if system:
        params["system"] = system
    t0 = time.time()
    resp = client.messages.create(**params)
    dt = time.time() - t0
    usage = {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens}
    return resp.content[0].text, usage, dt

def ask_local(prompt, system=None, **options):
    """Ask a local model a question using the Ollama API.

    Args:
        prompt (str): The question or prompt to ask the local model.
        **options: Additional keyword arguments for the API call.
        temprature, top_p, top_k, seed, num_predict, num_ctx, etc.

    Returns:
        tuple: A tuple containing the following elements:
            - text (str): The generated response from the local model.
            - usage_dict (dict): A dictionary with input and output token usage.
            - latency_seconds (float): The time taken for the API call in seconds.
    """
    import ollama
    t0=time.time()
    r = ollama.chat(model=OLLAMA_MODEL, messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content":prompt}], options=options)
    dt = time.time() - t0
    usage = {"input_tokens": r.get("prompt_eval_count"),
             "output_tokens": r.get("eval_count")}
    # print(r)
    return r["message"]["content"], usage, dt

def ask_gpt(prompt, system=None, **options):
    """Ask GPT a question using the OpenAI API.

    Args:
        prompt (str): The question or prompt to ask GPT.
        **options: Additional keyword arguments for the API call.

    Returns:
        tuple: A tuple containing the following elements:
            - text (str): The generated response from GPT.
            - usage_dict (dict): A dictionary with input and output token usage.
            - latency_seconds (float): The time taken for the API call in seconds.
    """
    import openai
    model = os.getenv("OPENAI_MODEL", "gpt-6-luna")
    client= openai.OpenAI()
    # print(system)
    t0 = time.time()
    # print(([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}])
    resp = client.chat.completions.create(
        model=model,
        messages=([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}],
        **options,
    )
    dt = time.time() - t0
    usage = {"input_tokens": resp.usage.prompt_tokens, "output_tokens": resp.usage.completion_tokens}
    # print(resp)
    return resp.choices[0].message.content, usage, dt

def chat_model(backend=None, temperature=0):
    """Langchain chat model used by LangGraph agents"""
    backend= backend or os.getenv("LLM_BACKEND", "openai")
    if backend == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=OPENAI_MODEL, temperature=temperature, max_tokens =1024)
    from langchain_ollama import ChatOllama
    return ChatOllama(model=OLLAMA_MODEL, temperature=temperature)
