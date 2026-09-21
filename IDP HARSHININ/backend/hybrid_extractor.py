
import spacy
import re


# ==============================
# 1. LOAD TRAINED NER MODEL
# ==============================

MODEL_DIR = "backend/ner_model"

nlp = spacy.load(MODEL_DIR)


# ==============================
# 2. MEDICAL INTERVENTIONS
# ==============================

INTERVENTIONS = [

    # --------------------------
    # Drugs
    # --------------------------

    "aspirin",
    "atorvastatin",
    "warfarin",
    "clopidogrel",
    "ticagrelor",
    "apixaban",
    "rivaroxaban",
    "losartan",
    "lisinopril",
    "amlodipine",
    "metoprolol",
    "metformin",
    "insulin",
    "empagliflozin",
    "dapagliflozin",
    "semaglutide",
    "liraglutide",
    "glipizide",
    "sitagliptin",
    "pembrolizumab",
    "nivolumab",
    "ipilimumab",
    "trastuzumab",
    "bevacizumab",
    "paclitaxel",
    "cisplatin",
    "carboplatin",
    "levodopa",
    "carbidopa",
    "donepezil",
    "memantine",
    "remdesivir",
    "molnupiravir",
    "ritonavir",
    "oseltamivir",
    "azithromycin",
    "amoxicillin",
    "eplontersen",
    "melatonin",
    "tadalafil",
    "fibrorestil",

    # --------------------------
    # Biological / nutritional
    # --------------------------

    "lactobacillus plantarum",
    "hawthorn vinegar",
    "black mulberry syrup",
    "green tea",

    # --------------------------
    # Lifestyle / behavioral
    # --------------------------

    "low-carbohydrate diet",
    "low-carbohydrate diets",
    "structured lifestyle intervention",
    "structured yoga-based lifestyle programme",
    "yoga-based intervention",
    "yoga-based lifestyle intervention",
    "traditional chinese exercise",
    "kuanle equipment exercise",
    "standard diabetes education",
    "standard digital diabetes education",
    "digital structured education program integrated with behavioral nudge tools",
    "cgm-guided personalized lifestyle coaching",
    "fully automated mhealth intervention",
    "ai-based diabetes prevention program",
    "healthcoach-assisted lifestyle intervention program",
    "antenatal milk expression",
    "control diet",

    # --------------------------
    # Devices / procedures
    # --------------------------

    "continuous glucose monitoring",
    "cgm alone",
    "penile traction",
    "andropenis extender",
    "closed reduction and percutaneous fixation",
    "open reduction and internal fixation",
    "crpf",
    "orif",
    "aid",
    "omnipod 5 automated insulin delivery (aid) system",
    "glp-1ras",
    "dpp-4is",

    # --------------------------
    # Other trial interventions
    # --------------------------

    "water",
    "100% fruit juice",
    "glucose-based sports drink",
]


# ==============================
# 3. MEDICAL DISEASES
# ==============================

DISEASES = [

    "hypertension",
    "type 2 diabetes",
    "cardiovascular disease",
    "diabetes",
    "gdm",
    "type 2 diabetes mellitus",
    "prediabetes",
    "hiv",
    "obesity",
    "peyronie's disease",
    "chronic kidney disease",
    "hereditary transthyretin amyloidosis",
    "polyneuropathy",
    "gestational diabetes mellitus",
    "stage iii periodontitis",
    "type 1 diabetes",
    "end-stage kidney disease",
    "heart failure",
]


# ==============================
# 4. MEDICAL ENDPOINTS
# ==============================

ENDPOINTS = [

    # --------------------------
    # Cardiovascular outcomes
    # --------------------------

    "cardiovascular events",
    "major adverse cardiovascular events",
    "myocardial infarction",
    "stroke",
    "mortality",
    "survival",
    "adverse events",
    "hospitalization",
    "death-inclusive composite",

    # --------------------------
    # General clinical outcomes
    # --------------------------

    "quality of life",
    "diabetes quality of life-brief",
    "response",
    "disability",
    "physical functioning",
    "nutritional status",
    "cost of care",
    "satisfaction",

    # --------------------------
    # Diabetes / glycemic outcomes
    # --------------------------

    "blood glucose levels",
    "blood glucose",
    "blood pressure",
    "glycemic metrics",
    "glycemic control",
    "glycemic outcomes",
    "glycemic variability",
    "hba1c",
    "fpg",
    "fasting plasma glucose",
    "fasting blood sugar",
    "2-h ogtt glucose",
    "bmi",
    "body mass index",
    "weight loss",
    "physical activity",
    "anthropometric measures",
    "diabetes risk reduction",
    "diabetes distress",

    # --------------------------
    # Glucose monitoring
    # --------------------------

    "time in range",
    "time above range",
    "mean sensor glucose",
    "tbr70",
    "tar180",
    "hyperglycemic exposure",
    "hypoglycemia confidence scale",
    "glucose responses",
    "total urine volume",

    # --------------------------
    # Neurological outcomes
    # --------------------------

    "neuropathy measures",
    "neuropathy impairment",
    "neuropathy symptom and change",
    "polyneuropathy disability",
    "autonomic dysfunction",
    "autonomic function",
    "walking speed",

    # --------------------------
    # Vascular / endothelial
    # --------------------------

    "endothelial function",
    "rhi",
    "flow-mediated dilatation",
    "arterial stiffness",
    "vascular ageing markers",
    "e-selectin",
    "icam-1",
    "p-selectin",
    "vcam-1",

    # --------------------------
    # Lipid / metabolic outcomes
    # --------------------------

    "lipid profile",
    "lipid profiles",
    "glycaemic and lipid profiles",
    "triglyceride levels",
    "polyunsaturated fatty acids",
    "monounsaturated fatty acids",
    "serum phospholipid fatty acids",
    "desaturase activities",

    # --------------------------
    # Renal / laboratory outcomes
    # --------------------------

    "renal function",
    "serum transthyretin levels",
    "serum 25(oh)d",
    "oxidative stress",

    # --------------------------
    # Oral health outcomes
    # --------------------------

    "oral mucositis",
    "oral health-related quality of life",
    "pocket depth",
    "clinical attachment loss",
    "gingival index",

    # --------------------------
    # Peyronie's disease outcomes
    # --------------------------

    "curvature change",
    "iief-ef",

    # --------------------------
    # Orthopedic outcomes
    # --------------------------

    "radiological union",
    "clinical function",
    "postoperative complications",
    "wound infection",
    "malunion",
    "non-union",
    "hardware discomfort",
    "deep venous thrombosis",

    # --------------------------
    # Breastfeeding outcomes
    # --------------------------

    "prenatal breastfeeding self-efficacy",
    "breastfeeding self-efficacy",
    "early exclusive breastfeeding",
    "exclusive breastfeeding rates",
    "delayed onset of lactogenesis ii",
    "lactogenesis onset",
    "time to lactogenesis onset",
    "breastfeeding behavior prediction indicators",
    "neonatal outcomes",

    # --------------------------
    # Other outcomes
    # --------------------------

    "social support",
]


# ==============================
# 5. SAMPLE SIZE RULES
# ==============================

SAMPLE_PATTERNS = [

    r"\bn\s*=\s*[\d,]+\b",

    r"\bN\s*=\s*[\d,]+\b",

    r"\b[\d,]+\s+(?:patients|participants|subjects|individuals|people|women|adults)\b",

    r"\btotal\s+of\s+[\d,]+\b",

    r"\benrolled\s+[\d,]+\b",
]


# ==============================
# 6. FIND DICTIONARY MATCHES
# ==============================

def find_dictionary_matches(text, terms, label):

    matches = []

    for term in terms:

        # Escape special characters
        pattern = re.escape(term)

        # Allow spaces or newlines between words
        pattern = pattern.replace(r"\ ", r"\s+")

        for match in re.finditer(
            pattern,
            text,
            re.IGNORECASE
        ):

            matches.append({
                # Convert newlines/multiple spaces to one space
                "text": " ".join(match.group().split()),

                "label": label,

                "start": match.start(),

                "end": match.end()
            })

    return matches


# ==============================
# 7. FIND SAMPLE SIZES
# ==============================

def find_sample_sizes(text):

    matches = []

    for pattern in SAMPLE_PATTERNS:

        for match in re.finditer(
            pattern,
            text,
            re.IGNORECASE
        ):

            matches.append({

                "text": " ".join(match.group().split()),

                "label": "SAMPLE_SIZE",

                "start": match.start(),

                "end": match.end()
            })

    return matches


# ==============================
# 8. REMOVE OVERLAPPING ENTITIES
# ==============================

def remove_overlaps(entities):

    # Prefer longer matches
    entities = sorted(
        entities,
        key=lambda x: (x["end"] - x["start"]),
        reverse=True
    )

    final = []

    for entity in entities:

        overlap = False

        for existing in final:

            if (
                entity["start"] < existing["end"]
                and entity["end"] > existing["start"]
            ):

                overlap = True
                break

        if not overlap:
            final.append(entity)

    return sorted(
        final,
        key=lambda x: x["start"]
    )


# ==============================
# 9. HYBRID EXTRACTION
# ==============================

def extract_entities(text):

    doc = nlp(text)

    entities = []

    # --------------------------
    # ML NER entities
    # --------------------------

    for ent in doc.ents:

        entities.append({

            "text": " ".join(ent.text.split()),

            "label": ent.label_,

            "start": ent.start_char,

            "end": ent.end_char
        })


    # --------------------------
    # Intervention dictionary
    # --------------------------

    entities.extend(

        find_dictionary_matches(

            text,

            INTERVENTIONS,

            "INTERVENTION"
        )
    )


    # --------------------------
    # Disease dictionary
    # --------------------------

    entities.extend(

        find_dictionary_matches(

            text,

            DISEASES,

            "DISEASE"
        )
    )


    # --------------------------
    # Endpoint dictionary
    # --------------------------

    entities.extend(

        find_dictionary_matches(

            text,

            ENDPOINTS,

            "ENDPOINT"
        )
    )


    # --------------------------
    # Sample-size rules
    # --------------------------

    entities.extend(

        find_sample_sizes(text)

    )


    # --------------------------
    # Remove exact duplicates
    # --------------------------

    unique = {}

    for entity in entities:

        key = (

            entity["start"],

            entity["end"],

            entity["label"]
        )

        unique[key] = entity

    entities = list(
        unique.values()
    )


    # --------------------------
    # Remove overlapping entities
    # --------------------------

    entities = remove_overlaps(
        entities
    )

    return entities


# ==============================
# 10. TEST
# ==============================

if __name__ == "__main__":

    text = """
    A randomized clinical trial evaluated Metformin in 350 patients
    with type 2 diabetes. The study measured HbA1c and blood glucose
    levels after 24 weeks of treatment.
    """

    print("\n==============================")
    print("HYBRID NER TEST")
    print("==============================")

    print("\nInput:")
    print(text)

    print("\nDetected entities:")

    entities = extract_entities(text)

    for entity in entities:

        print(
            f"{entity['text']} --> "
            f"{entity['label']}"
        )

    print("\n==============================")

