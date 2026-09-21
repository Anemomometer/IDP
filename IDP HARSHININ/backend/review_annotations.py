import json

INPUT_FILE = "data/pre_annotated_pubmed.json"


# ------------------------------------------------------------
# Load pre-annotated data
# ------------------------------------------------------------

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    abstracts = json.load(file)


print("=" * 70)
print("CLINICAL TRIAL NER - ANNOTATION REVIEW")
print("=" * 70)

print(f"Total abstracts: {len(abstracts)}")


# ------------------------------------------------------------
# Review each abstract
# ------------------------------------------------------------

for index, abstract in enumerate(abstracts, start=1):

    pmid = abstract["pmid"]
    text = abstract["text"]
    entities = abstract["entities"]

    print("\n")
    print("=" * 70)
    print(f"ABSTRACT {index}/{len(abstracts)}")
    print(f"PMID: {pmid}")
    print("=" * 70)

    print("\nTEXT:")
    print("-" * 70)
    print(text)

    print("\nDETECTED ENTITIES:")
    print("-" * 70)

    if not entities:
        print("No entities detected.")

    else:

        for i, entity in enumerate(entities, start=1):

            entity_text = entity["text"]
            label = entity["label"]
            start = entity["start"]
            end = entity["end"]

            print(
                f"{i}. {entity_text} "
                f"--> {label} "
                f"(position {start}-{end})"
            )

    # --------------------------------------------------------
    # Wait before moving to next abstract
    # --------------------------------------------------------

    print("\nPress ENTER to review the next abstract...")
    input()


print("\n")
print("=" * 70)
print("REVIEW COMPLETED")
print("=" * 70)