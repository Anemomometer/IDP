from hybrid_extractor import extract_entities
from relation_extraction import extract_relations
from assertion_detection import detect_assertion


def run_pipeline(text):

    # -----------------------------
    # STEP 1: NER
    # -----------------------------
    entities = extract_entities(text)

    # Convert entities into dictionary format
    entity_list = []

    for ent in entities:
        entity_list.append({
            "text": ent["text"],
            "label": ent["label"],
            "start": ent["start"],
            "end": ent["end"]
        })

    # -----------------------------
    # STEP 2: Assertion Detection
    # -----------------------------
    for entity in entity_list:
        entity["assertion"] = detect_assertion(text, entity)

    # -----------------------------
    # STEP 3: Relation Extraction
    # -----------------------------
    relations = extract_relations(text,entity_list)

    # -----------------------------
    # FINAL RESULT
    # -----------------------------
    return {
        "text": text,
        "entities": entity_list,
        "relations": relations
    }


if __name__ == "__main__":

    text = """
    A randomized clinical trial evaluated Metformin in 350 patients
    with type 2 diabetes. The study measured HbA1c and blood glucose
    levels after 24 weeks of treatment.
    """

    result = run_pipeline(text)

    print("\n================================")
    print("MULTI-TASK NLP PIPELINE")
    print("================================")

    print("\nTEXT:")
    print(result["text"])

    print("\nENTITIES + ASSERTIONS:")

    for entity in result["entities"]:
        print(
            entity["text"],
            "-->",
            entity["label"],
            "-->",
            entity["assertion"]
        )

    print("\nRELATIONS:")

    for relation in result["relations"]:
        print(
            relation["source"],
            "--[",
            relation["relation"],
            "]-->",
            relation["target"]
        )

    print("\n================================")