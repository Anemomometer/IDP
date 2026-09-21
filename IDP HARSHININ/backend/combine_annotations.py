import json
import os


BATCH1_FILE = os.path.join(
    "data",
    "cleaned_annotations.json"
)

BATCH2_FILE = os.path.join(
    "data",
    "cleaned_annotations_batch2.json"
)

OUTPUT_FILE = os.path.join(
    "data",
    "combined_annotations.json"
)


def main():

    print("Loading Batch 1...")
    with open(BATCH1_FILE, "r", encoding="utf-8") as file:
        batch1 = json.load(file)

    print("Batch 1 abstracts:", len(batch1))

    print("\nLoading Batch 2...")
    with open(BATCH2_FILE, "r", encoding="utf-8") as file:
        batch2 = json.load(file)

    print("Batch 2 abstracts:", len(batch2))

    # Combine both datasets
    combined = batch1 + batch2

    # Check for duplicate PMIDs
    pmids = [record["pmid"] for record in combined]

    duplicates = {
        pmid for pmid in pmids
        if pmids.count(pmid) > 1
    }

    if duplicates:
        print("\nWARNING: Duplicate PMIDs found:")
        for pmid in duplicates:
            print(pmid)
    else:
        print("\nNo duplicate PMIDs found.")

    # Sort entities inside every abstract
    for record in combined:
        record["entities"].sort(
            key=lambda x: (x["start"], x["end"])
        )

    # Count entities
    counts = {
        "DISEASE": 0,
        "INTERVENTION": 0,
        "SAMPLE_SIZE": 0,
        "ENDPOINT": 0
    }

    for record in combined:
        for entity in record["entities"]:
            label = entity["label"]

            if label in counts:
                counts[label] += 1

    # Save
    os.makedirs("data", exist_ok=True)

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            combined,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\n====================================")
    print("COMBINATION COMPLETE")
    print("====================================")

    print("Total abstracts:", len(combined))

    print("\nENTITY COUNTS:")

    for label, count in counts.items():
        print(f"{label}: {count}")

    print("\nTotal entities:", sum(counts.values()))

    print("\nSaved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()