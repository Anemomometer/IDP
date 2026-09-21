import json
import re
from pathlib import Path


# ---------------------------------------------------------
# FILE PATHS
# ---------------------------------------------------------

INPUT_FILE = Path("data/pre_annotated_pubmed.json")
OUTPUT_FILE = Path("data/cleaned_annotations.json")


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def remove_entity(entities, text, label=None, occurrence=None):
    """
    Remove an entity matching the given text and optional label.

    occurrence:
        None -> remove all matching occurrences
        0,1,2... -> remove only that occurrence
    """

    matches = []

    for i, ent in enumerate(entities):
        if ent["text"].lower() == text.lower():
            if label is None or ent["label"] == label:
                matches.append(i)

    if occurrence is not None:
        if occurrence < len(matches):
            del entities[matches[occurrence]]
    else:
        for i in reversed(matches):
            del entities[i]


def change_label(entities, text, old_label, new_label, occurrence=None):
    """
    Change the label of an existing entity.
    """

    matches = []

    for i, ent in enumerate(entities):
        if (
            ent["text"].lower() == text.lower()
            and ent["label"] == old_label
        ):
            matches.append(i)

    if occurrence is not None:
        if occurrence < len(matches):
            entities[matches[occurrence]]["label"] = new_label
    else:
        for i in matches:
            entities[i]["label"] = new_label


def add_entity(text, entities, phrase, label):
    """
    Add every occurrence of phrase that is not already present.
    """

    for match in re.finditer(
        re.escape(phrase),
        text,
        flags=re.IGNORECASE
    ):
        start = match.start()
        end = match.end()

        # Avoid duplicate / overlapping entities
        overlap = False

        for ent in entities:
            if not (end <= ent["start"] or start >= ent["end"]):
                overlap = True
                break

        if not overlap:
            entities.append({
                "text": text[start:end],
                "label": label,
                "start": start,
                "end": end
            })


def sort_entities(entities):
    """
    Keep entities ordered by their position in the abstract.
    """

    entities.sort(key=lambda x: (x["start"], x["end"]))


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)


print("=" * 60)
print("CLEANING ANNOTATIONS")
print("=" * 60)


# ---------------------------------------------------------
# PROCESS EACH ABSTRACT
# ---------------------------------------------------------

for record in data:

    pmid = str(record["pmid"])
    text = record["text"]
    entities = record["entities"]

    print(f"\nProcessing PMID: {pmid}")

    # =====================================================
    # ABSTRACT 1 — PMID 42699213
    # =====================================================

    if pmid == "42699213":

        # Blood pressure was a diagnostic/risk variable,
        # not a trial endpoint.
        remove_entity(
            entities,
            "blood pressure",
            "ENDPOINT"
        )

        # BMI was a baseline/risk characteristic here,
        # not the trial endpoint.
        remove_entity(
            entities,
            "body mass index",
            "ENDPOINT"
        )

        # Myocardial infarction is being discussed as
        # an outcome in this abstract.
        change_label(
            entities,
            "myocardial infarction",
            "DISEASE",
            "ENDPOINT"
        )

        # Stroke is being discussed as an outcome.
        change_label(
            entities,
            "stroke",
            "DISEASE",
            "ENDPOINT"
        )


    # =====================================================
    # ABSTRACT 4 — PMID 42695340
    # =====================================================

    elif pmid == "42695340":

        # These standalone "diabetes" mentions occur inside
        # phrases such as diabetes education/self-management.
        # The specific disease entity is already captured.
        remove_entity(
            entities,
            "diabetes",
            "DISEASE"
        )

        # Missing intervention entities.
        add_entity(
            text,
            entities,
            "digital structured education program integrated with behavioral nudge tools",
            "INTERVENTION"
        )

        add_entity(
            text,
            entities,
            "standard digital diabetes education",
            "INTERVENTION"
        )


    # =====================================================
    # ABSTRACT 6 — PMID 42692503
    # =====================================================

    elif pmid == "42692503":

        # Generic diabetes mention in "diabetes care".
        remove_entity(
            entities,
            "diabetes",
            "DISEASE"
        )

        # "mortality" occurs in a background statement,
        # not as a trial endpoint.
        remove_entity(
            entities,
            "mortality",
            "ENDPOINT"
        )


    # =====================================================
    # ABSTRACT 7 — PMID 42687658
    # =====================================================

    elif pmid == "42687658":

        # Generic diabetes mention inside
        # "diabetes self-management".
        remove_entity(
            entities,
            "diabetes",
            "DISEASE"
        )


    # =====================================================
    # ABSTRACT 8 — PMID 42685343
    # =====================================================

    elif pmid == "42685343":

        # These generic diabetes mentions are inside
        # intervention-related phrases.
        remove_entity(
            entities,
            "diabetes",
            "DISEASE"
        )

        # Baseline BMI is a predictor/characteristic,
        # not an endpoint in this abstract.
        remove_entity(
            entities,
            "BMI",
            "ENDPOINT"
        )


    # =====================================================
    # ABSTRACT 9 — PMID 42682442
    # =====================================================

    elif pmid == "42682442":

        # Generic diabetes mention inside
        # "diabetes related distress".
        remove_entity(
            entities,
            "diabetes",
            "DISEASE"
        )


    # =====================================================
    # ABSTRACT 10 — PMID 42681636
    # =====================================================

    elif pmid == "42681636":

        # Add abbreviation for gestational diabetes mellitus.
        add_entity(
            text,
            entities,
            "GDM",
            "DISEASE"
        )

        # Add abbreviation for antenatal milk expression.
        add_entity(
            text,
            entities,
            "AME",
            "INTERVENTION"
        )


    # -----------------------------------------------------
    # SORT
    # -----------------------------------------------------

    sort_entities(entities)


# ---------------------------------------------------------
# SAVE CLEANED DATA
# ---------------------------------------------------------

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(
        data,
        f,
        indent=2,
        ensure_ascii=False
    )


# ---------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------

total_entities = sum(
    len(record["entities"])
    for record in data
)

print("\n" + "=" * 60)
print("CLEANING COMPLETE")
print("=" * 60)

print(f"Total abstracts: {len(data)}")
print(f"Total entities after cleaning: {total_entities}")

print("\nSaved cleaned dataset to:")
print(OUTPUT_FILE)