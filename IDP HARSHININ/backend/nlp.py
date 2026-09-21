import json
import random
import os

import spacy
from spacy.training import Example
from spacy.util import minibatch


# =========================================================
# FILES
# =========================================================

DATA_FILE = "data/combined_annotations_fixed.json"
MODEL_DIR = "backend/ner_model"


# =========================================================
# LOAD DATA
# =========================================================

with open(DATA_FILE, "r", encoding="utf-8") as file:
    training_data = json.load(file)

print("Total training examples:", len(training_data))


# =========================================================
# REMOVE DUPLICATE ENTITIES
# =========================================================

duplicates_removed = 0

for record in training_data:

    unique_entities = []
    seen = set()

    for entity in record["entities"]:

        key = (
            entity["start"],
            entity["end"],
            entity["label"]
        )

        if key in seen:
            duplicates_removed += 1
        else:
            seen.add(key)
            unique_entities.append(entity)

    record["entities"] = unique_entities


print("Duplicate entities removed:", duplicates_removed)


# =========================================================
# CREATE BLANK MODEL
# =========================================================

nlp = spacy.blank("en")

ner = nlp.add_pipe("ner")


# =========================================================
# ENTITY LABELS
# =========================================================

labels = [
    "DISEASE",
    "INTERVENTION",
    "SAMPLE_SIZE",
    "ENDPOINT"
]

for label in labels:
    ner.add_label(label)


# =========================================================
# CREATE TRAINING EXAMPLES
# =========================================================

examples = []

for item in training_data:

    text = item["text"]

    entities = []

    for entity in item["entities"]:

        entities.append(
            (
                entity["start"],
                entity["end"],
                entity["label"]
            )
        )

    doc = nlp.make_doc(text)

    example = Example.from_dict(
        doc,
        {
            "entities": entities
        }
    )

    examples.append(example)


# =========================================================
# INITIALIZE MODEL
# =========================================================

nlp.initialize(
    lambda: examples
)


# =========================================================
# TRAIN MODEL
# =========================================================

print("\nStarting NER training...\n")

for epoch in range(40):

    random.shuffle(examples)

    losses = {}

    batches = minibatch(
        examples,
        size=4
    )

    for batch in batches:

        nlp.update(
            batch,
            drop=0.2,
            losses=losses
        )

    print(
        f"Epoch {epoch + 1}: {losses}"
    )


# =========================================================
# SAVE MODEL
# =========================================================

os.makedirs(MODEL_DIR, exist_ok=True)

nlp.to_disk(MODEL_DIR)


print("\n====================================")
print("TRAINING COMPLETE")
print("====================================")

print("Model saved to:")
print(MODEL_DIR)