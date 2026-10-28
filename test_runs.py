
# How tokenizer stores tokens in the r50k_base.tiktoken file
# import base64

# with open("C:\\Users\\palak.munet\\Downloads\\r50k_base.tiktoken", encoding="utf-8") as f:
#     for _ in range(500):
#         token, rank = f.readline().strip().split()
#         print(base64.b64decode(token), rank)


import tiktoken

enc = tiktoken.get_encoding("r50k_base")

for word in ["all", "allow", "almost", "small"]:
    ids = enc.encode(word)
    pieces = [enc.decode([i]) for i in ids]
    print(word, "->", pieces, ids)