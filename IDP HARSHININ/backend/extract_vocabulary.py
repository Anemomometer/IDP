import json
import re
from collections import Counter

DATA_FILE = "data/combined_annotations_unique.json"

with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

vocabulary = {
    "DISEASE": Counter(),
    "INTERVENTION": Counter(),
    "ENDPOINT": Counter(),
    "SAMPLE_SIZE": Counter()
}

for item in data:
    for entity in item["entities"]:
        text = entity["text"].strip().lower()
        label = entity["label"]

        if label in vocabulary:
            vocabulary[label][text] += 1

print("\n================================")
print("CLINICAL TRIAL VOCABULARY")
print("================================")

for label, terms in vocabulary.items():

    print(f"\n========== {label} ==========")

    for term, count in terms.most_common():
        print(f"{term} --> {count}")