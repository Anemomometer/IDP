import json
import os
import re
import spacy

INPUT_FILE = "data/combined_annotations.json"
OUTPUT_FILE = "data/combined_annotations_fixed.json"

nlp = spacy.blank("en")


def replace_entity(record, old_text, new_text, label, occurrence=0):
    """
    Replace one specific entity annotation.
    """

    text = record["text"]

    matches = list(
        re.finditer(
            re.escape(old_text),
            text,
            re.IGNORECASE
        )
    )

    if occurrence >= len(matches):
        return False

    match = matches[occurrence]

    record["entities"].append({
        "text": match.group(),
        "label": label,
        "start": match.start(),
        "end": match.end()
    })

    return True


def remove_entity(record, entity_text, label):
    """
    Remove matching annotation(s).
    """

    record["entities"] = [
        e for e in record["entities"]
        if not (
            e["text"].lower() == entity_text.lower()
            and e["label"] == label
        )
    ]


def fix_record(record):

    pmid = record["pmid"]

    # ---------------------------------------------------------
    # PMID 42695340
    # ---------------------------------------------------------

    if pmid == "42695340":

        # Change 146 -> n=146
        for e in record["entities"]:
            if e["text"] == "146" and e["label"] == "SAMPLE_SIZE":
                start = record["text"].find("n=146")

                if start != -1:
                    e["text"] = "n=146"
                    e["start"] = start
                    e["end"] = start + len("n=146")

        # Change 147 -> n=147
        for e in record["entities"]:
            if e["text"] == "147" and e["label"] == "SAMPLE_SIZE":
                start = record["text"].find("n=147")

                if start != -1:
                    e["text"] = "n=147"
                    e["start"] = start
                    e["end"] = start + len("n=147")


    # ---------------------------------------------------------
    # PMID 42687658
    # ---------------------------------------------------------

    elif pmid == "42687658":

        for e in record["entities"]:

            if e["text"] == "34" and e["label"] == "SAMPLE_SIZE":

                # Find the nearest n=34 after/before current position
                old_start = e["start"]

                matches = list(
                    re.finditer(r"n=34", record["text"])
                )

                if matches:

                    best = min(
                        matches,
                        key=lambda m: abs(m.start() - old_start)
                    )

                    e["text"] = best.group()
                    e["start"] = best.start()
                    e["end"] = best.end()


    # ---------------------------------------------------------
    # PMID 42682442
    # ---------------------------------------------------------

    elif pmid == "42682442":

        for e in record["entities"]:

            if e["label"] == "SAMPLE_SIZE":

                old_start = e["start"]

                # Find nearest n=number
                matches = list(
                    re.finditer(
                        r"n=\d+",
                        record["text"],
                        re.IGNORECASE
                    )
                )

                if matches:

                    best = min(
                        matches,
                        key=lambda m: abs(m.start() - old_start)
                    )

                    # Only repair if it is close to original position
                    if abs(best.start() - old_start) <= 5:

                        e["text"] = best.group()
                        e["start"] = best.start()
                        e["end"] = best.end()


    # ---------------------------------------------------------
    # PMID 42680257
    # ---------------------------------------------------------

    elif pmid == "42680257":

        text = record["text"]

        for e in record["entities"]:

            if e["label"] == "INTERVENTION":

                if e["text"].lower() == "low-carbohydrate diet":

                    start = text.lower().find(
                        "low-carbohydrate diets"
                    )

                    if start != -1:
                        e["text"] = text[
                            start:start + len("low-carbohydrate diets")
                        ]
                        e["start"] = start
                        e["end"] = start + len(
                            "low-carbohydrate diets"
                        )

                elif e["text"].lower() == "lcd":

                    start = text.lower().find("lcds")

                    if start != -1:
                        e["text"] = text[
                            start:start + len("lcds")
                        ]
                        e["start"] = start
                        e["end"] = start + len("lcds")


        # Fix saturated fatty acids annotations
        for e in record["entities"]:

            if (
                e["label"] == "ENDPOINT"
                and e["text"].lower() == "saturated fatty acids"
            ):

                old_start = e["start"]

                if old_start < 1000:

                    new_text = "monounsaturated fatty acids"

                else:

                    new_text = "polyunsaturated fatty acids"

                start = text.find(new_text)

                if start != -1:

                    e["text"] = new_text
                    e["start"] = start
                    e["end"] = start + len(new_text)


    # ---------------------------------------------------------
    # PMID 42679726
    # ---------------------------------------------------------

    elif pmid == "42679726":

        text = record["text"]

        for e in record["entities"]:

            if (
                e["label"] == "ENDPOINT"
                and e["text"] == "P-Selectin"
            ):

                start = text.find("P-Selectin")

                if start != -1:

                    e["start"] = start
                    e["end"] = start + len("P-Selectin")
                    e["text"] = "P-Selectin"


    # ---------------------------------------------------------
    # PMID 42679373
    # ---------------------------------------------------------

    elif pmid == "42679373":

        text = record["text"]

        for e in record["entities"]:

            if (
                e["label"] == "ENDPOINT"
                and e["text"].lower() == "lipid profile"
            ):

                start = text.lower().find("lipid profiles")

                if start != -1:

                    e["text"] = text[
                        start:start + len("lipid profiles")
                    ]

                    e["start"] = start
                    e["end"] = start + len("lipid profiles")


    # Sort entities
    record["entities"].sort(
        key=lambda x: (x["start"], x["end"])
    )


def check_alignment(record):

    doc = nlp.make_doc(record["text"])

    bad = []

    for entity in record["entities"]:

        span = doc.char_span(
            entity["start"],
            entity["end"],
            label=entity["label"],
            alignment_mode="strict"
        )

        if span is None:
            bad.append(entity)

    return bad


def main():

    print("Loading combined dataset...")

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        data = json.load(file)

    print("Total abstracts:", len(data))

    print("\nFixing misaligned annotations...")

    for record in data:
        fix_record(record)

    print("\nChecking alignment...")

    total_bad = 0

    for record in data:

        bad = check_alignment(record)

        if bad:

            print(
                f"\nPMID {record['pmid']} "
                f"has {len(bad)} problem(s):"
            )

            for e in bad:

                print(
                    f"  {e['text']} "
                    f"({e['start']}, {e['end']}) "
                    f"-> {e['label']}"
                )

            total_bad += len(bad)

    os.makedirs("data", exist_ok=True)

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\n====================================")
    print("FIX COMPLETE")
    print("====================================")

    print("Total remaining misaligned:", total_bad)

    print("\nSaved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()