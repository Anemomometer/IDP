import re


# ==========================================
# ASSERTION DETECTION
# ==========================================

def detect_assertion(text, entity):

    # Get the sentence containing the entity
    start = entity["start"]
    end = entity["end"]

    sentence_start = text.rfind(".", 0, start) + 1
    sentence_end = text.find(".", end)

    if sentence_end == -1:
        sentence_end = len(text)

    sentence = text[sentence_start:sentence_end].strip()

    # Convert to lowercase for checking
    lower_sentence = sentence.lower()

    # ======================================
    # NEGATED
    # ======================================

    negation_patterns = [
        r"\bno\b",
        r"\bnot\b",
        r"\bdid not\b",
        r"\bdoes not\b",
        r"\bwas not\b",
        r"\bwere not\b",
        r"\bwithout\b",
        r"\bfailed to\b",
        r"\bneither\b"
    ]

    for pattern in negation_patterns:

        if re.search(pattern, lower_sentence):

            return "ABSENT_NEGATED"

    # ======================================
    # CONDITIONAL
    # ======================================

    conditional_patterns = [
        r"\bmay\b",
        r"\bmight\b",
        r"\bcould\b",
        r"\bpotentially\b",
        r"\bpossible\b",
        r"\bpossibly\b",
        r"\bsuggests?\b",
        r"\bif\b"
    ]

    for pattern in conditional_patterns:

        if re.search(pattern, lower_sentence):

            return "CONDITIONAL"

    # ======================================
    # POSITIVE
    # ======================================

    positive_patterns = [
        r"\breduced\b",
        r"\bincreased\b",
        r"\bimproved\b",
        r"\bsignificant\b",
        r"\beffective\b",
        r"\bbeneficial\b",
        r"\bassociated with\b",
        r"\bresulted in\b",
        r"\bdecreased\b",
        r"\bimproved\b"
    ]

    for pattern in positive_patterns:

        if re.search(pattern, lower_sentence):

            return "PRESENT_POSITIVE"

    # ======================================
    # DEFAULT
    # ======================================

    return "PRESENT_POSITIVE"


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    test_cases = [

        "Metformin reduced blood glucose levels.",

        "Metformin did not reduce blood glucose levels.",

        "Metformin may reduce blood glucose levels.",

    ]

    print("\n================================")
    print("ASSERTION DETECTION TEST")
    print("================================")

    for text in test_cases:

        entity_start = text.find("Metformin")

        entity = {
            "text": "Metformin",
            "label": "INTERVENTION",
            "start": entity_start,
            "end": entity_start + len("Metformin")
        }

        assertion = detect_assertion(text, entity)

        print("\nText:")
        print(text)

        print("Assertion:", assertion)

    print("\n================================")