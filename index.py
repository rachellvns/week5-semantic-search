from gc import enable
from pathlib import Path
from store import client, models, MODEL, ensure_collection

ensure_collection("docs")
points = []

for n, p in enumerate(sorted(Path("corpus").glob("*.*"))):
    text = p.read_text(errors="ignore")[:2000]
    points.append(models.PointStruct(
        id=n,
        vector=models.Document(text=text, model=MODEL),
        payload={"text": text, "source":p.name,
                 "type": p.suffix.lstrip("."),
                 "user_id": "userA" if n % 2 == 0 else "userB"}
        ))
    client.upsert("docs", points=points)
    print(f"indexed: {len(points)} documents")