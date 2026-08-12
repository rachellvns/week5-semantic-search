from store import MODEL
from fastembed import TextEmbedding
import numpy as np

embedder = TextEmbedding(model_name=MODEL)

def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def explain_match(query: str, doc_text: str):
    sentences = [s.strip() for s in doc_text.replace("\n", " ").split(".") if s.strip()]
    
    query_vec = list(embedder.embed([query]))[0]
    sentence_vecs = list(embedder.embed(sentences))
    
    scored = [(cosine(query_vec, sv), s) for sv, s in zip(sentence_vecs, sentences)]
    scored.sort(reverse=True)
    
    print(f"Query: '{query}'\n")
    for score, sentence in scored[:5]:
        print(f"{score:.3f}  {sentence}")

# Example usage
doc_text = open("corpus/doc04.txt").read()
explain_match("相比于维持睡眠，我更难入睡", doc_text)