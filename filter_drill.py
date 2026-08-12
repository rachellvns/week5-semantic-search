from pyexpat import model

from store import client, models, MODEL

query_text = "how do I get more of my medication"

print("Unfiltered:")
hits = client.query_points("docs",
                           query=models.Document(text=query_text, model=MODEL),
                           limit=5).points
for h in hits:
    print(h.score, h.payload["user_id"], h.payload["source"])
    
print("\nFiltered (user A):")
flt = models.Filter(must=[models.FieldCondition(key="user_id", match=models.MatchValue(value="userA"))])
hits = client.query_points("docs",
                           query=models.Document(text=query_text, model=MODEL),
                           query_filter=flt, limit=5).points
for h in hits:
    print(h.score, h.payload["user_id"], h.payload["source"])
    
print("\nFiltered (user B)")
flt = models.Filter(must=[models.FieldCondition(
    key="user_id", match=models.MatchValue(value="userB"))])
hits = client.query_points("docs",
    query=models.Document(text=query_text, model=MODEL),
    query_filter=flt, limit=5).points
for h in hits:
    print(h.score, h.payload["user_id"], h.payload["source"])