import sys
from store import client, models, MODEL

query = "".join(sys.argv[1:])
hits = client.query_points("docs",
                           query=models.Document(text=query, model=MODEL), limit=5).points
for h in hits:
    print(f"{h.score: .3f} {h.payload['source']}")
    print("    ", h.payload["text"][:100].replace("\n", " "), "\n")