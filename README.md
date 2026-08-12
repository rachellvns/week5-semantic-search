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

## Cross-language probe  
### Model used: bge-small-en-v1.5
Two queries were tested in English, Bahasa Indonesia, and Mandarin Chinese to evaluate whether the model retrieves the correct document regardless of query language.  
### Query 1: "Drink more water"  
| Language | Query | Top Result | Score | Strongest Sentence Match |
|---|---|---|---|---|
| English | "drink more water" | doc17 | 0.647 | "Plan: Oral fluids and light meals" (0.745) — accurate |
| Indonesian | "minum lebih banyak air" | doc13 | 0.511 | "Review inhaler technique during next in-person visit" (0.536) — irrelevant |
| Chinese | "多喝水" | doc12 | 0.614 | "Tan" (0.638, provider surname) — irrelevant; "Advice: Increase oral fluids" (0.625) — accurate, but not the top contributor |  

**Observation:**  
The English query correctly and confidently retrieved a relevant document (doc17, hydration advice) with a clear top sentence match. The Indonesian query scored notably lower (0.511 vs 0.647) and retrieved a completely unrelated document (doc13, asthma inhaler technique). The model failed to recognize "air" (water) as semantically related to hydration advice in English text. The Chinese query also failed at the sentence level: its highest-scoring "match" was a provider's surname ("Tan"), not the actual hydration sentence, even though a relevant document (doc12) was retrieved by coincidence. The retrieval was not driven by genuine understanding of "多喝水" (drink more water).  
### Query 2: "I struggle more with getting to sleep than staying asleep"  
| Language | Query | Top Result | Score | Strongest Sentence Match |
|---|---|---|---|---|
| English | "I struggle more with getting to sleep than staying asleep" | doc11 | 0.710 | "She reports difficulty falling asleep rather than staying asleep" (0.746) — highly accurate |
| Indonesian | "saya lebih susah mulai tidur daripada mempertahankan tidur" | doc07 | 0.602 | "TM Case 0007 Date: 5 April 2026 Grace W" (0.636) — meaningless (matched metadata, not content) |
| Chinese | "相比于维持睡眠，我更难入睡" | doc04 | 0.602 | "Arrange F2F BP assessment" (0.636) — meaningless |  

**Observation:** The English query was a near-perfect match, both in overall score (0.710) and in identifying the exact corresponding sentence in doc11. Both the Indonesian and Chinese paraphrases of the identical meaning scored substantially lower (0.602 vs 0.710) and, critically, matched completely unrelated documents with the "strongest" contributing sentences being administrative metadata (a patient's name, a visit date) rather than any clinically relevant text. This shows the model is not recognizing semantic content in these queries at all; the retrieved documents appear essentially random relative to query meaning.  

### Discussion: why bge-m3 would change this
'bge-small-en-v1.5' was trained exclusively on English text, so it has no learned representation aligning non-English queries with semantically equivalent English content. The results above confirmed this, where both non-English queries not only scored lower than their English equivalents, but were driven by arbitrary sentence matches (patient names, unrelated administrative text) rather than any real understanding of query meaning.  

'bge-m3', by contrast, is explicitly trained as a multilingual model across 100+ languages, including cross-lingual retrieval objectives where a query in one language is trained to embed close to matching content in another. Based on this corpus's results, switching to 'bge-m3' would likely be necessary for any production telehealth use case serving Bahasa Indonesia/Melayu or Chinese-speaking patients, since the current model's cross-language retrieval is effectively non-functional.

## Filter drill
Scenario: Each indexed document was assigned a 'user_id' ("userA" or "userB", alternating by document index) in its Qdrant payload, simulating a two-user corpus for access-control testing.

### How each document got a 'user_id'
Document access:
user A (12 files): doc01.txt, doc02.txt, doc03.txt, doc04_copy.md, doc06.txt, doc08.txt, doc10.txt, doc12.txt, doc14.txt, doc16.txt, doc18.txt, doc20.txt  

user B (11 files): doc01_copy.md, doc02_copy.md, doc04.txt, doc05.txt, doc07.txt, doc09.txt, doc11.txt, doc13.txt, doc15.txt, doc17.txt, doc19.txt  

This produces a roughly even, reproducible 50/50 split across all 23 documents, simulating two separate users' document sets without needing real multi-user data.  

### Where 'user_id' lives
Each document's user_id is stored as a field in its Qdrant payload (metadata attached to the vector), alongside the existing text, source, and type fields:  

payload={"text": text, "source": p.name,  
         "type": p.suffix.lstrip("."),  
         "user_id": "userA" if n % 2 == 0 else "userB"}

### How a search is restricted to one user
A Qdrant Filter is built specifying that the 'user_id' field must equal a given value:  

flt = models.Filter(must=[models.FieldCondition(  
    key="user_id", match=models.MatchValue  
    (value="userA"))])  

This filter is passed into query_points() via query_filter=flt.  
Unlike a ranking boost or preference, this is a hard constraint: Qdrant excludes any point whose payload doesn't satisfy the filter before returning results regardless of how high that point's semantic similarity score is.