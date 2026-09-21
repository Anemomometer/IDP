import spacy
from hybrid_extractor import extract_entities


# ==========================================
# LOAD SPACY MODEL
# ==========================================

nlp = spacy.load("backend/ner_model")

# Add sentence detection
if "sentencizer" not in nlp.pipe_names:
    nlp.add_pipe("sentencizer")


# ==========================================
# RELATION EXTRACTION
# ==========================================

def extract_relations(text, entities):

    doc = nlp(text)

    relations = []

    # Remember the most recent intervention
    current_intervention = None

    for sent in doc.sents:

        sentence_entities = []

        for entity in entities:

            if (
                entity["start"] >= sent.start_char
                and entity["end"] <= sent.end_char
            ):
                sentence_entities.append(entity)

        interventions = [
            e for e in sentence_entities
            if e["label"] == "INTERVENTION"
        ]

        diseases = [
            e for e in sentence_entities
            if e["label"] == "DISEASE"
        ]

        sample_sizes = [
            e for e in sentence_entities
            if e["label"] == "SAMPLE_SIZE"
        ]

        endpoints = [
            e for e in sentence_entities
            if e["label"] == "ENDPOINT"
        ]

        # ----------------------------------
        # Remember intervention
        # ----------------------------------

        if interventions:
            current_intervention = interventions[0]

        # ----------------------------------
        # INTERVENTION → DISEASE
        # ----------------------------------

        for intervention in interventions:

            for disease in diseases:

                relations.append({
                    "source": intervention["text"],
                    "source_label": "INTERVENTION",
                    "relation": "TREATS",
                    "target": disease["text"],
                    "target_label": "DISEASE"
                })

        # ----------------------------------
        # INTERVENTION → SAMPLE SIZE
        # ----------------------------------

        for intervention in interventions:

            for sample in sample_sizes:

                relations.append({
                    "source": intervention["text"],
                    "source_label": "INTERVENTION",
                    "relation": "TESTED_IN_COHORT",
                    "target": sample["text"],
                    "target_label": "SAMPLE_SIZE"
                })

        # ----------------------------------
        # INTERVENTION → ENDPOINT
        # ----------------------------------

        if endpoints and current_intervention:

            for endpoint in endpoints:

                relations.append({
                    "source": current_intervention["text"],
                    "source_label": "INTERVENTION",
                    "relation": "MEASURED_BY",
                    "target": endpoint["text"],
                    "target_label": "ENDPOINT"
                })

    # ======================================
    # REMOVE DUPLICATES
    # ======================================

    unique_relations = []
    seen = set()

    for relation in relations:

        key = (
            relation["source"],
            relation["relation"],
            relation["target"]
        )

        if key not in seen:

            seen.add(key)
            unique_relations.append(relation)

    return unique_relations


# ==========================================
# TEST COMPLETE PIPELINE
# ==========================================
if __name__ == "__main__":

    text = """
    A clinical trial evaluated Aspirin in 200 patients
    with heart disease. Another clinical trial evaluated
    Metformin in 350 patients with type 2 diabetes.
    """

    # Automatically extract entities
    entities = extract_entities(text)

    print("\n================================")
    print("MULTIPLE INTERVENTION TEST")
    print("================================")

    print("\nDetected entities:")

    for entity in entities:
        print(
            f"{entity['text']} --> "
            f"{entity['label']}"
        )

    # Extract relations
    relations = extract_relations(text, entities)

    print("\nDetected relations:")

    for relation in relations:
        print(
            f"{relation['source']} "
            f"--[{relation['relation']}]--> "
            f"{relation['target']}"
        )

    print("\n================================")