def fixed_chunks(text, size=800, overlap=100):
    step = size - overlap
    return [text[i: i+size] for i in range(0, len(text), step) if text[i: i+size].strip()]

def recursive_chunks(text, size=800, seps=("\n## ", "\n\n", "\n", ". ", " ")):
    """Split on the biggest natural boundary first; only go finer if a piece is still too long."""
    text = text.strip()
    if len(text) <= size:
        return [text] if text else []

    if not seps:
        return [text[i:i + size] for i in range(0, len(text), size)]

    sep, rest = seps[0], seps[1:]

    out, cur = [], ""
    for part in text.split(sep):
        cand = (cur + sep + part) if cur else part
        if len(cand) <= size:
            cur = cand
        else:
            if cur:
                out.append(cur)
            if len(part) > size:
                out.extend(recursive_chunks(part, size, rest))
                cur = ""
            else:
                cur = part
        if cur:
            out.append(cur)
    return out

        