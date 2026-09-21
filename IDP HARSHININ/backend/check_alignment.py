import json
import spacy
from spacy.training import offsets_to_biluo_tags


INPUT_FILE = "data/combined_annotations.json"


# Blank English model is enough for checking token alignment
nlp = spacy.blank("en")


with open(INPUT_FILE, "r", encoding="utf-8") as file:
    data = json.load(file)


total_entities = 0
misaligned_entities = 0


print("Checking entity alignment...\n")


for record in data:

    text = record["text"]

    entities = [
        (
            entity["start"],
            entity["end"],
            entity["label"]
        )
        for entity in record["entities"]
    ]

    total_entities += len(entities)

    doc = nlp.make_doc(text)

    tags = offsets_to_biluo_tags(
        doc,
        entities
    )

    if "-" in tags:

        print("=" * 60)
        print("PMID:", record["pmid"])

        print("\nText:")
        print(text[:200], "...")

        print("\nProblematic entities:")

        for entity in record["entities"]:

            start = entity["start"]
            end = entity["end"]
            label = entity["label"]

            entity_doc = nlp.make_doc(
                text[start:end]
            )

            # Check whether this individual span
            # aligns with token boundaries
            span = doc.char_span(
                start,
                end,
                label=label,
                alignment_mode="strict"
            )

            if span is None:

                misaligned_entities += 1

                print(
                    f"  {entity['text']} "
                    f"({start}, {end}) "
                    f"-> {label}"
                )


print("\n" + "=" * 60)
print("ALIGNMENT CHECK COMPLETE")
print("=" * 60)

print("Total entities:", total_entities)
print("Misaligned entities:", misaligned_entities)
print(
    "Aligned entities:",
    total_entities - misaligned_entities
)