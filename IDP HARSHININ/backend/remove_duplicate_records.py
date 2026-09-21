import json

INPUT_FILE = "data/combined_annotations_fixed.json"
OUTPUT_FILE = "data/combined_annotations_unique.json"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

unique_data = []
seen_pmids = set()

for item in data:
    pmid = item["pmid"]

    if pmid not in seen_pmids:
        unique_data.append(item)
        seen_pmids.add(pmid)

print("Original records:", len(data))
print("Unique records:", len(unique_data))
print("Duplicates removed:", len(data) - len(unique_data))

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(unique_data, f, indent=2, ensure_ascii=False)

print("\nSaved to:", OUTPUT_FILE)