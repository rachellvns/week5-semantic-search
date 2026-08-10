# CHANGED: was `import sys` before. argparse replaces manual sys.argv slicing.
# Why: sys.argv[1:] only works for plain positional words - there's no clean
# way to add optional flags like --type with it. argparse handles flags,
# positional args, help text (-h), and error messages automatically.
import argparse
from store import client, models, MODEL

# search logic is now wrapped in a function instead of living directly at the top of the script.
def search(query: str, doc_type: str | None = None):
    flt = None
    if doc_type:
        flt = models.Filter(must=[models.FieldCondition(
            key="type",
            match=models.MatchValue(value=doc_type))])
    return client.query_points("docs",
        query=models.Document(text=query, model=MODEL),
        query_filter=flt, limit=5).points

if __name__ == "__main__":
    """replaces query = " ".join(sys.argv[1:]).
    Why: nargs="+" tells argparse  to collect one or more words into a list
    for this positional argument - same end result as before (you can still
    type multiple words with no quotes), but now argparse can tell the
    difference between query words and flags like --type. """
    parser = argparse.ArgumentParser()
    parser.add_argument("query", nargs="+", help="search query text")
    
    # dest="doc_type" means the parsed value is stored as args.doc_type. 
    # default=None means if you don't pass --type, filtering is skipped (same as calling search(query) with no second argument).
    parser.add_argument("--type", dest="doc_type", default=None,
                         help="filter by file type, e.g. txt or md")
    
    args = parser.parse_args()

    # Now joins args.query (the list argparse collected) instead of raw sys.argv.
    # sys.argv[1:] would have included --type and "txt" as if they were query words. 
    # args.query only contains the words argparse identified as the actual query, correctly separated from --type.
    query_text = " ".join(args.query)
    hits = search(query_text, doc_type=args.doc_type)

    for h in hits:
        print(f"{h.score:.3f}  {h.payload['source']}")
        print("   ", h.payload["text"][:100].replace("\n", " "), "\n")