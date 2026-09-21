import json
import os
import re


INPUT_FILE = os.path.join("data", "pre_annotated_pubmed_batch2.json")
OUTPUT_FILE = os.path.join("data", "cleaned_annotations_batch2.json")


def remove_entity(record, entity_text, label):
    """
    Remove an entity if its text and label match.
    """
    new_entities = []

    for entity in record["entities"]:
        if not (
            entity["text"].lower() == entity_text.lower()
            and entity["label"] == label
        ):
            new_entities.append(entity)

    record["entities"] = new_entities


def change_label(record, entity_text, old_label, new_label):
    """
    Change the label of matching entities.
    """
    for entity in record["entities"]:
        if (
            entity["text"].lower() == entity_text.lower()
            and entity["label"] == old_label
        ):
            entity["label"] = new_label


def add_entity(record, phrase, label):
    """
    Add all exact occurrences of a phrase.
    Offsets are calculated automatically.
    """
    text = record["text"]

    pattern = re.compile(re.escape(phrase), re.IGNORECASE)

    existing = {
        (e["start"], e["end"], e["label"])
        for e in record["entities"]
    }

    for match in pattern.finditer(text):
        start = match.start()
        end = match.end()

        # Check for exact duplicate
        if (start, end, label) in existing:
            continue

        # Avoid overlapping another entity
        overlap = False

        for entity in record["entities"]:
            if start < entity["end"] and end > entity["start"]:
                overlap = True
                break

        if overlap:
            continue

        record["entities"].append({
            "text": match.group(),
            "label": label,
            "start": start,
            "end": end
        })

        existing.add((start, end, label))


def clean_record(record):
    pmid = record["pmid"]

    # =========================================================
    # 1. PMID 42709983
    # =========================================================
    if pmid == "42709983":

        add_entity(
            record,
            "Traditional Chinese Exercise",
            "INTERVENTION"
        )

        add_entity(
            record,
            "Kuanle Equipment Exercise",
            "INTERVENTION"
        )

        add_entity(
            record,
            "2-h OGTT glucose",
            "ENDPOINT"
        )

        add_entity(
            record,
            "serum 25(OH)D",
            "ENDPOINT"
        )

    # =========================================================
    # 2. PMID 42706409
    # =========================================================
    elif pmid == "42706409":

        add_entity(
            record,
            "stage III periodontitis",
            "DISEASE"
        )

        add_entity(
            record,
            "non-surgical periodontal treatment",
            "INTERVENTION"
        )

        add_entity(
            record,
            "PRL levels",
            "ENDPOINT"
        )

        add_entity(
            record,
            "pocket depth",
            "ENDPOINT"
        )

        add_entity(
            record,
            "clinical attachment loss",
            "ENDPOINT"
        )

        add_entity(
            record,
            "gingival index",
            "ENDPOINT"
        )

    # =========================================================
    # 3. PMID 42704279
    # =========================================================
    elif pmid == "42704279":

        add_entity(
            record,
            "Peyronie's disease",
            "DISEASE"
        )

        add_entity(
            record,
            "Fibrorestil",
            "INTERVENTION"
        )

        add_entity(
            record,
            "tadalafil",
            "INTERVENTION"
        )

        add_entity(
            record,
            "penile traction",
            "INTERVENTION"
        )

        add_entity(
            record,
            "Andropenis extender",
            "INTERVENTION"
        )

        add_entity(
            record,
            "curvature change",
            "ENDPOINT"
        )

        add_entity(
            record,
            "PDQ changes",
            "ENDPOINT"
        )

        add_entity(
            record,
            "IIEF-EF",
            "ENDPOINT"
        )

        add_entity(
            record,
            "satisfaction",
            "ENDPOINT"
        )

        add_entity(
            record,
            "adverse events",
            "ENDPOINT"
        )

    # =========================================================
    # 4. PMID 42699213
    # Same correction as Batch 1
    # =========================================================
    elif pmid == "42699213":

        remove_entity(
            record,
            "blood pressure",
            "ENDPOINT"
        )

        remove_entity(
            record,
            "body mass index",
            "ENDPOINT"
        )

        change_label(
            record,
            "myocardial infarction",
            "DISEASE",
            "ENDPOINT"
        )

        change_label(
            record,
            "stroke",
            "DISEASE",
            "ENDPOINT"
        )

    # =========================================================
    # 5. PMID 42697907
    # Current annotations are good.
    # =========================================================
    elif pmid == "42697907":
        pass

    # =========================================================
    # 6. PMID 42697856
    # Current annotations are good.
    # =========================================================
    elif pmid == "42697856":
        pass

    # =========================================================
    # 7. PMID 42695340
    # =========================================================
    elif pmid == "42695340":

        remove_entity(
            record,
            "diabetes",
            "DISEASE"
        )

        add_entity(
            record,
            "digital structured education program integrated with behavioral nudge tools",
            "INTERVENTION"
        )

        add_entity(
            record,
            "standard digital diabetes education",
            "INTERVENTION"
        )

    # =========================================================
    # 8. PMID 42694165
    # Current annotations are good.
    # =========================================================
    elif pmid == "42694165":
        pass

    # =========================================================
    # 9. PMID 42692503
    # =========================================================
    elif pmid == "42692503":

        remove_entity(
            record,
            "diabetes",
            "DISEASE"
        )

        remove_entity(
            record,
            "mortality",
            "ENDPOINT"
        )

    # =========================================================
    # 10. PMID 42687658
    # =========================================================
    elif pmid == "42687658":

        remove_entity(
            record,
            "diabetes",
            "DISEASE"
        )

    # =========================================================
    # 11. PMID 42685343
    # =========================================================
    elif pmid == "42685343":

        remove_entity(
            record,
            "diabetes",
            "DISEASE"
        )

        remove_entity(
            record,
            "BMI",
            "ENDPOINT"
        )

    # =========================================================
    # 12. PMID 42682442
    # =========================================================
    elif pmid == "42682442":

        remove_entity(
            record,
            "diabetes",
            "DISEASE"
        )

    # =========================================================
    # 13. PMID 42681636
    # =========================================================
    elif pmid == "42681636":

        add_entity(
            record,
            "GDM",
            "DISEASE"
        )

        add_entity(
            record,
            "AME",
            "INTERVENTION"
        )

    # =========================================================
    # 14. PMID 42680257
    # =========================================================
    elif pmid == "42680257":

        remove_entity(
            record,
            "mortality",
            "ENDPOINT"
        )

        add_entity(
            record,
            "low-carbohydrate diet",
            "INTERVENTION"
        )

        add_entity(
            record,
            "LCD",
            "INTERVENTION"
        )

        add_entity(
            record,
            "control diet",
            "INTERVENTION"
        )

        add_entity(
            record,
            "serum phospholipid fatty acids",
            "ENDPOINT"
        )

        add_entity(
            record,
            "saturated fatty acids",
            "ENDPOINT"
        )

        add_entity(
            record,
            "monounsaturated fatty acids",
            "ENDPOINT"
        )

        add_entity(
            record,
            "polyunsaturated fatty acids",
            "ENDPOINT"
        )

        add_entity(
            record,
            "desaturase activities",
            "ENDPOINT"
        )

    # =========================================================
    # 15. PMID 42679726
    # =========================================================
    elif pmid == "42679726":

        add_entity(
            record,
            "semaglutide",
            "INTERVENTION"
        )

        add_entity(
            record,
            "empagliflozin",
            "INTERVENTION"
        )

        # The paper spells this number out
        add_entity(
            record,
            "One hundred and twenty",
            "SAMPLE_SIZE"
        )

        add_entity(
            record,
            "RHI",
            "ENDPOINT"
        )

        add_entity(
            record,
            "E-Selectin",
            "ENDPOINT"
        )

        add_entity(
            record,
            "ICAM-1",
            "ENDPOINT"
        )

        add_entity(
            record,
            "P-Selectin",
            "ENDPOINT"
        )

        add_entity(
            record,
            "VCAM-1",
            "ENDPOINT"
        )

        add_entity(
            record,
            "endothelial function",
            "ENDPOINT"
        )

    # =========================================================
    # 16. PMID 42679373
    # =========================================================
    elif pmid == "42679373":

        remove_entity(
            record,
            "mortality",
            "ENDPOINT"
        )

        add_entity(
            record,
            "melatonin",
            "INTERVENTION"
        )

        add_entity(
            record,
            "lipid profile",
            "ENDPOINT"
        )

        add_entity(
            record,
            "triglyceride levels",
            "ENDPOINT"
        )

        add_entity(
            record,
            "renal function",
            "ENDPOINT"
        )

    # =========================================================
    # 17. PMID 42675283
    # =========================================================
    elif pmid == "42675283":

        add_entity(
            record,
            "closed reduction and percutaneous fixation",
            "INTERVENTION"
        )

        add_entity(
            record,
            "open reduction and internal fixation",
            "INTERVENTION"
        )

        add_entity(
            record,
            "CRPF",
            "INTERVENTION"
        )

        add_entity(
            record,
            "ORIF",
            "INTERVENTION"
        )

        add_entity(
            record,
            "50",
            "SAMPLE_SIZE"
        )

        add_entity(
            record,
            "radiological union",
            "ENDPOINT"
        )

        add_entity(
            record,
            "clinical function",
            "ENDPOINT"
        )

        add_entity(
            record,
            "AOFAS score",
            "ENDPOINT"
        )

        add_entity(
            record,
            "postoperative complications",
            "ENDPOINT"
        )

        add_entity(
            record,
            "wound infection",
            "ENDPOINT"
        )

        add_entity(
            record,
            "malunion",
            "ENDPOINT"
        )

        add_entity(
            record,
            "non-union",
            "ENDPOINT"
        )

        add_entity(
            record,
            "hardware discomfort",
            "ENDPOINT"
        )

        add_entity(
            record,
            "deep venous thrombosis",
            "ENDPOINT"
        )

        # 13 was an outcome count, not the trial sample size
        remove_entity(
            record,
            "13",
            "SAMPLE_SIZE"
        )

    # =========================================================
    # 18. PMID 42672944
    # =========================================================
    elif pmid == "42672944":

        remove_entity(
            record,
            "BMI",
            "ENDPOINT"
        )

        add_entity(
            record,
            "100% fruit juice",
            "INTERVENTION"
        )

        add_entity(
            record,
            "glucose-based sports drink",
            "INTERVENTION"
        )

        add_entity(
            record,
            "water",
            "INTERVENTION"
        )

        add_entity(
            record,
            "rehydration efficacy",
            "ENDPOINT"
        )

        add_entity(
            record,
            "glucose responses",
            "ENDPOINT"
        )

        add_entity(
            record,
            "total urine volume",
            "ENDPOINT"
        )

    # =========================================================
    # 19. PMID 42671087
    # =========================================================
    elif pmid == "42671087":

        # Remove partial/nested annotations before adding
        # the complete intervention/outcome names.
        remove_entity(
            record,
            "Insulin",
            "INTERVENTION"
        )

        remove_entity(
            record,
            "Diabetes",
            "DISEASE"
        )

        remove_entity(
            record,
            "Quality of Life",
            "ENDPOINT"
        )

        add_entity(
            record,
            "Omnipod 5 Automated Insulin Delivery (AID) System",
            "INTERVENTION"
        )

        add_entity(
            record,
            "AID",
            "INTERVENTION"
        )

        add_entity(
            record,
            "75",
            "SAMPLE_SIZE"
        )

        add_entity(
            record,
            "time in range",
            "ENDPOINT"
        )

        add_entity(
            record,
            "time above range",
            "ENDPOINT"
        )

        add_entity(
            record,
            "mean sensor glucose",
            "ENDPOINT"
        )

        add_entity(
            record,
            "Diabetes Quality of Life-brief",
            "ENDPOINT"
        )

        add_entity(
            record,
            "Hypoglycemia Confidence Scale",
            "ENDPOINT"
        )

        add_entity(
            record,
            "adverse events",
            "ENDPOINT"
        )

    # =========================================================
    # 20. PMID 42669711
    # =========================================================
    elif pmid == "42669711":

        add_entity(
            record,
            "end-stage kidney disease",
            "DISEASE"
        )

        add_entity(
            record,
            "GLP-1RAs",
            "INTERVENTION"
        )

        add_entity(
            record,
            "DPP-4is",
            "INTERVENTION"
        )

        add_entity(
            record,
            "ischemic cardiovascular events",
            "ENDPOINT"
        )

        add_entity(
            record,
            "heart failure exacerbations",
            "ENDPOINT"
        )

        add_entity(
            record,
            "all-cause mortality",
            "ENDPOINT"
        )

        add_entity(
            record,
            "death-inclusive composite",
            "ENDPOINT"
        )


def main():

    print("Loading Batch 2...")

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    print(f"Total abstracts: {len(data)}")

    for record in data:
        clean_record(record)

        # Always keep entities sorted by their position
        record["entities"].sort(
            key=lambda x: (x["start"], x["end"])
        )

    total_entities = sum(
        len(record["entities"])
        for record in data
    )

    counts = {
        "DISEASE": 0,
        "INTERVENTION": 0,
        "SAMPLE_SIZE": 0,
        "ENDPOINT": 0
    }

    for record in data:
        for entity in record["entities"]:
            if entity["label"] in counts:
                counts[entity["label"]] += 1

    os.makedirs("data", exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\n====================================")
    print("BATCH 2 CLEANING COMPLETE")
    print("====================================")

    print("Total entities:", total_entities)

    print("\nENTITY COUNTS:")

    for label, count in counts.items():
        print(f"{label}: {count}")

    print("\nSaved cleaned dataset to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()