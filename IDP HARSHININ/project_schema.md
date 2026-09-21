# Clinical Trial NLP - Annotation Schema

## Named Entity Recognition (NER)

The system will initially extract four types of entities.

### 1. DISEASE
Medical disease, disorder, condition, or health problem being studied.

Examples:
- heart failure
- type 2 diabetes
- non-small cell lung cancer

### 2. DRUG
Drug, medication, treatment, or intervention used in the clinical trial.

Examples:
- Semaglutide
- Pembrolizumab
- Empagliflozin

### 3. SAMPLE_SIZE
Number of participants/patients enrolled in the clinical trial.

Examples:
- 529
- 500
- 1200

### 4. ENDPOINT
Clinical outcome, measurement, or endpoint being evaluated.

Examples:
- cardiovascular events
- overall survival
- blood glucose levels


## Relation Extraction (RE)

The system will initially identify:

### TREATS
DRUG → DISEASE

Example:
Semaglutide → TREATS → heart failure

### TESTED_IN
DRUG → SAMPLE_SIZE

Example:
Semaglutide → TESTED_IN → 529 patients

### MEASURED_BY
DRUG → ENDPOINT

Example:
Semaglutide → MEASURED_BY → cardiovascular events


## Assertion Detection

The system will classify statements as:

### PRESENT_POSITIVE
The condition/treatment/outcome is positively stated.

### ABSENT_NEGATED
The statement contains a negation.

### CONDITIONAL
The statement is conditional or uncertain.