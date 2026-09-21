import json
from hybrid_extractor import extract_entities

# Load real PubMed abstracts
with open("data/pubmed_abstracts_batch2.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Test first 5 abstracts
for i, item in enumerate(data[:5], start=1):

    pmid = item.get("pmid") or item.get("PMID")

    # Try the possible text fields
    text = (
        item.get("abstract")
        or item.get("abstract_text")
        or item.get("text")
        or item.get("Abstract")
    )

    print("\n" + "=" * 60)
    print(f"ABSTRACT {i}")
    print(f"PMID: {pmid}")
    print("=" * 60)

    if not text:
        print("No abstract text found.")
        print("Available fields:", item.keys())
        continue

    entities = extract_entities(text)

    if not entities:
        print("No entities found.")
        continue

    for entity in entities:
        print(
            f"{entity['text']} --> "
            f"{entity['label']}"
        )