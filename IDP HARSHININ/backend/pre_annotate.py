import json
import re


INPUT_FILE = "data/pubmed_abstracts_batch2.json"
OUTPUT_FILE = "data/pre_annotated_pubmed_batch2.json"


# ============================================================
# ENTITY DICTIONARIES
# ============================================================

INTERVENTIONS = [
    # Drugs / medicines
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

    # Other interventions
    "lactobacillus plantarum",
    "hawthorn vinegar",
    "black mulberry syrup",
    "green tea",
    "structured yoga-based lifestyle programme",
    "yoga-based lifestyle intervention",
    "yoga-based intervention",
    "CGM-guided personalized lifestyle coaching",
    "continuous glucose monitoring",
    "cgm alone",
    "standard diabetes education",
    "ai-based diabetes prevention program",
    "fully automated mhealth intervention",
    "healthcoach-assisted lifestyle intervention program",
    "structured lifestyle intervention",
    "antenatal milk expression",
]


DISEASES = [
    # Cardiovascular
    "hypertension",
    "heart failure",
    "myocardial infarction",
    "cardiovascular disease",
    "coronary artery disease",
    "coronary heart disease",
    "atrial fibrillation",
    "stroke",

    # Diabetes / metabolic
    "gestational diabetes mellitus",
    "type 2 diabetes mellitus",
    "type 1 diabetes mellitus",
    "type 2 diabetes",
    "type 1 diabetes",
    "diabetes mellitus",
    "diabetes",
    "prediabetes",
    "obesity",

    # Cancer
    "cancer",
    "lung cancer",
    "non-small cell lung cancer",
    "small cell lung cancer",
    "breast cancer",
    "prostate cancer",
    "colorectal cancer",

    # Neurological
    "hereditary transthyretin amyloidosis",
    "polyneuropathy",
    "alzheimer disease",
    "alzheimer's disease",
    "parkinson disease",
    "parkinson's disease",
    "epilepsy",
    "multiple sclerosis",

    # Infectious
    "hiv",
    "influenza",
    "covid-19",
    "covid",
    "hepatitis",
    "tuberculosis",

    # Other
    "asthma",
    "chronic kidney disease",
    "chronic obstructive pulmonary disease",
    "copd",
]


ENDPOINTS = [
    # Cardiovascular
    "major adverse cardiovascular events",
    "cardiovascular events",
    "myocardial infarction",
    "stroke",
    "mortality",

    # General clinical outcomes
    "overall survival",
    "progression-free survival",
    "disease-free survival",
    "adverse events",
    "quality of life",
    "clinical response",
    "treatment response",
    "symptom improvement",
    "hospitalization",
    "hospital admissions",

    # Diabetes / metabolic
    "blood glucose levels",
    "blood glucose",
    "blood pressure",
    "glycemic control",
    "glycemic outcomes",
    "glycemic variability",
    "hemoglobin a1c",
    "hba1c",
    "fasting plasma glucose",
    "fasting blood sugar",
    "fpg",
    "body mass index",
    "bmi",
    "weight loss",
    "physical activity",
    "diabetes risk reduction",
    "hyperglycemic exposure",
    "tbr70",
    "tar180",
    "anthropometric measures",
    "diabetes distress",
    "glycaemic and lipid profiles",

    # Neurology
    "neuropathy impairment",
    "neuropathy symptom and change",
    "polyneuropathy disability",
    "physical functioning",
    "nutritional status",
    "serum transthyretin levels",
    "autonomic dysfunction",
    "disability",
    "walking speed",

    # Vascular / lifestyle
    "endothelial function",
    "flow-mediated dilatation",
    "arterial stiffness",
    "vascular ageing markers",
    "autonomic function",
    "oxidative stress",
    "cost of care",

    # Oral health
    "oral mucositis",
    "oral health-related quality of life",

    # Breastfeeding / maternal outcomes
    "prenatal breastfeeding self-efficacy",
    "breastfeeding self-efficacy",
    "lactogenesis onset",
    "early exclusive breastfeeding",
    "time to lactogenesis onset",
    "delayed onset of lactogenesis ii",
    "exclusive breastfeeding rates",
    "social support",
    "breastfeeding behavior prediction indicators",
    "maternal outcomes",
    "neonatal outcomes",
]


# ============================================================
# SAMPLE SIZE PATTERNS
# ============================================================

SAMPLE_PATTERNS = [

    # 120 participants
    r"\b(\d[\d,]*)\s+(?:patients|participants|subjects|individuals|people|women|adults)\b",

    # n=146 / n = 146
    r"\bn\s*=\s*(\d[\d,]*)\b",

    # N=146 / N = 146
    r"\bN\s*=\s*(\d[\d,]*)\b",

    # total of 248
    r"\btotal\s+of\s+(\d[\d,]*)\b",

    # total 248
    r"\btotal\s+(\d[\d,]*)\b",

    # enrolled 240
    r"\benrolled\s+(\d[\d,]*)\b",

    # included 149 participants
    r"\bincluded\s+(\d[\d,]*)\s+(?:patients|participants|subjects|individuals|people|women|adults)\b",
]


# ============================================================
# FIND DICTIONARY ENTITIES
# ============================================================

def find_entities(text, terms, label):

    entities = []

    # Longer phrases first
    sorted_terms = sorted(terms, key=len, reverse=True)

    for term in sorted_terms:

        pattern = r"\b" + re.escape(term) + r"\b"

        for match in re.finditer(pattern, text, re.IGNORECASE):

            entities.append({
                "text": match.group(),
                "label": label,
                "start": match.start(),
                "end": match.end()
            })

    return entities


# ============================================================
# FIND SAMPLE SIZES
# ============================================================

def find_sample_sizes(text):

    entities = []

    for pattern in SAMPLE_PATTERNS:

        for match in re.finditer(pattern, text, re.IGNORECASE):

            number = match.group(1)

            # Remove commas
            clean_number = number.replace(",", "")

            start = match.start(1)
            end = match.end(1)

            entities.append({
                "text": clean_number,
                "label": "SAMPLE_SIZE",
                "start": start,
                "end": end
            })

    return entities


# ============================================================
# REMOVE DUPLICATES
# ============================================================

def remove_duplicates(entities):

    unique = []
    seen = set()

    for entity in entities:

        key = (
            entity["start"],
            entity["end"],
            entity["label"]
        )

        if key not in seen:
            seen.add(key)
            unique.append(entity)

    return unique


# ============================================================
# REMOVE OVERLAPPING ENTITIES
# ============================================================

def remove_overlaps(entities):

    # Longer entities get priority
    entities = sorted(
        entities,
        key=lambda x: (
            -(x["end"] - x["start"]),
            x["start"]
        )
    )

    selected = []

    for entity in entities:

        overlap = False

        for existing in selected:

            if (
                entity["start"] < existing["end"]
                and entity["end"] > existing["start"]
            ):
                overlap = True
                break

        if not overlap:
            selected.append(entity)

    # Put them back in text order
    selected.sort(key=lambda x: x["start"])

    return selected


# ============================================================
# PROCESS ONE ABSTRACT
# ============================================================

def process_abstract(abstract):

    text = abstract["text"]

    entities = []

    entities.extend(
        find_entities(
            text,
            DISEASES,
            "DISEASE"
        )
    )

    entities.extend(
        find_entities(
            text,
            INTERVENTIONS,
            "INTERVENTION"
        )
    )

    entities.extend(
        find_entities(
            text,
            ENDPOINTS,
            "ENDPOINT"
        )
    )

    entities.extend(
        find_sample_sizes(text)
    )

    entities = remove_duplicates(entities)

    entities = remove_overlaps(entities)

    return {
        "pmid": abstract["pmid"],
        "text": text,
        "entities": entities
    }


# ============================================================
# MAIN
# ============================================================

def main():

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        abstracts = json.load(file)

    processed = []

    for abstract in abstracts:

        result = process_abstract(abstract)

        processed.append(result)

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            processed,
            file,
            indent=2,
            ensure_ascii=False
        )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    counts = {
        "DISEASE": 0,
        "INTERVENTION": 0,
        "SAMPLE_SIZE": 0,
        "ENDPOINT": 0
    }

    total_entities = 0

    for abstract in processed:

        for entity in abstract["entities"]:

            label = entity["label"]

            if label in counts:
                counts[label] += 1

            total_entities += 1

    print("\n")
    print("=" * 60)
    print("PRE-ANNOTATION COMPLETED")
    print("=" * 60)

    print(f"Total abstracts: {len(processed)}")
    print(f"Total detected entities: {total_entities}")

    print("\nENTITY COUNTS:")

    for label, count in counts.items():
        print(f"{label}: {count}")

    print("\nSaved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()