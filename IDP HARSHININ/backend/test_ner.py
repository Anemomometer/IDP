import spacy


# =========================================================
# LOAD TRAINED MODEL
# =========================================================

MODEL_DIR = "backend/ner_model"

nlp = spacy.load(MODEL_DIR)


# =========================================================
# TEST INPUT
# =========================================================

text = """
A randomized clinical trial evaluated Metformin in 350 patients
with type 2 diabetes. The study measured HbA1c and blood glucose
levels after 24 weeks of treatment.
"""


# =========================================================
# RUN NER
# =========================================================

doc = nlp(text)


# =========================================================
# DISPLAY RESULTS
# =========================================================

print("\n============================================================")
print("NER TEST")
print("============================================================")

print("\nInput text:")
print(text)

print("\nDetected entities:")

if doc.ents:

    for ent in doc.ents:
        print(
            f"{ent.text} --> {ent.label_}"
        )

else:

    print("No entities detected.")


# =========================================================
# EXPECTED ENTITIES
# =========================================================

print("\n============================================================")
print("EXPECTED ENTITIES")
print("============================================================")

print("Metformin --> INTERVENTION")
print("350 --> SAMPLE_SIZE")
print("type 2 diabetes --> DISEASE")
print("HbA1c --> ENDPOINT")
print("blood glucose levels --> ENDPOINT")


# =========================================================
# SIMPLE CHECK
# =========================================================

print("\n============================================================")
print("TEST COMPLETE")
print("============================================================")