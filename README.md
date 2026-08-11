## Neighbour Intuition (Key observations)
To understand why certain documents ranked where they did, each top-ranking document's text was split into sentences and each sentence was individually scored against the query (using the chunk_score.py script). This revealed several cases where the whole-document ranking did not reflect the strongest available sentence-level match.

### 1. Dilution effect
Query: "drink more water"  
doc11 ranked above doc12 (0.639 vs 0.612), despite doc12 containing a stronger direct sentence match ("Advice: Increase oral fluids", 0.801) than doc11's best match ("Recommendations: Reduce caffeine intake", 0.731). The surrounding text in doc12 likely diluted its overall document vector, pulling its whole-document score below a weaker but more topically "average" match in doc11.

### 2. Generic phrasing produces unreliable matches
Query: "come back for a check-up in 7 days"  
doc04 — the document containing the most literal source phrase ("Review in 1 week") — did not appear in the top 5 results at all. Instead, doc06 (diabetes follow-up) ranked 2nd, driven by a generic scheduling phrase ("Repeat HbA1c in 3 months") with no real relevance to the query's intent. Only doc02 (headache follow-up, "Return if headache persists >7 days") was a genuinely relevant match. This suggests that generic clinical scheduling language ("review in X") produces weak, easily-confused embeddings that don't reliably distinguish relevant from irrelevant documents.

### 3. Surface word overlap can outrank true semantic matches
Query: "stay away from milk products for a little while"  
doc14 (infant reflux, mentioning "drinking milk" in an unrelated context) ranked above doc17, despite doc17 containing a near-exact match ("Avoid dairy for the next few days", 0.885 sentence score). This indicates the model can be swayed by surface-level word overlap ("milk") over a stronger conceptual match ("dairy").

### 4. High-scoring false positives
Query: "no signs of throwing up, loose stools, skin irritation, or trouble breathing"  
The expected document (doc15, containing "No vomiting, diarrhoea, rash, or breathing difficulty reported") did not appear in the top 5 at all. The top-ranked result (doc17, 0.754) was instead driven by a weakly-relevant sentence ("No fever"). This is a clear example of a high-looking score not corresponding to true relevance,
reinforcing that raw score thresholds alone are not a reliable relevance filter for negation-heavy, multi-symptom queries.