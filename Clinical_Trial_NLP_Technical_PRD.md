# Technical PRD — Clinical Trial NLP
### Automated Information Extraction from Clinical Trial Literature
**Patent Reference:** US20250252261A1
**Version:** 1.0

---

## 1. Purpose

This document specifies the technical architecture, models, data pipeline, storage schema, APIs, and evaluation methodology for the Clinical Trial NLP system. It is the engineering counterpart to the product PRD and is intended for the developers building the pipeline, database, and backend services.

---

## 2. System Overview

The system ingests PubMed abstracts, runs them through a single shared biomedical language model that jointly performs three NLP tasks, and writes structured, confidence-scored results to a database that powers a review dashboard.

**High-level data flow:**

```
NCBI PubMed API
      │
      ▼
Ingestion Service (fetch + normalize abstract text)
      │
      ▼
Shared Biomedical Encoder
      │
   ┌──┴────────────────┐
   ▼        ▼           ▼
  NER   Relation     Assertion
        Extraction   Detection
   │        │           │
   └────────┴───────────┘
      │
      ▼
Post-processing / Confidence Scoring
      │
      ▼
SQLite Database (entities, relations, assertions)
      │
      ▼
API Layer (serves React dashboard)
```

---

## 3. Model Architecture

### 3.1 Shared Encoder
- A single pretrained biomedical language model backbone (e.g., a BERT-family biomedical encoder) is shared across all three tasks.
- **Rationale:** shared biomedical context benefits all three heads; reduces total parameter count and inference cost vs. three independent models.
- Each task is implemented as a separate "head" on top of the shared encoder's contextual token embeddings.

### 3.2 Task Heads

**a) NER Head**
- Token classification (e.g., BIO tagging scheme).
- Target entity types: Disease, Drug, Sample Size, Endpoint/Outcome.
- Output: entity spans with type label + confidence score (softmax probability of predicted tag sequence, or per-token confidence aggregated over the span).

**b) Relation Extraction Head**
- Operates on pairs of entities identified by the NER head within the same abstract (or same sentence, depending on design decision made during Core NLP phase).
- Target relation types: Drug→Disease, Drug→Cohort, Outcome links.
- Output: relation type + confidence score per entity pair.

**c) Assertion Detection Head**
- Operates on each extracted relation (or entity mention) to classify assertion status.
- Target classes: Positive, Negated, Conditional.
- Output: assertion class + confidence score.

### 3.3 Training Data
- Hand-annotated gold-standard subset of PubMed abstracts, labeled for entities, relations, and assertions.
- Held-out test split reserved strictly for evaluation (not used in training or hyperparameter tuning).
- Recommend stratified splitting to ensure all entity/relation/assertion classes are represented in both train and test sets.

### 3.4 Multi-task Training Considerations
- Joint loss = weighted sum of NER loss + RE loss + AD loss.
- Task loss weights should be tunable; monitor per-task validation metrics independently to avoid one task dominating shared encoder updates.
- Consider staged training (pretrain encoder on NER, then jointly fine-tune with RE/AD heads) if joint training underperforms.

---

## 4. Ingestion Pipeline

### 4.1 PubMed API Integration
- Source: NCBI E-utilities (ESearch to find PMIDs matching a query, EFetch to retrieve abstract XML).
- Ingestion modes:
  - **On-demand:** user submits a search term via dashboard; system queries PubMed live and processes returned abstracts.
  - **Batch/scheduled:** periodic pull of new abstracts matching saved queries (optional, stretch goal).
- Respect NCBI rate limits (recommend E-utilities API key usage and throttling, e.g., max 3–10 requests/sec depending on key status).

### 4.2 Text Normalization
- Strip XML/HTML artifacts from EFetch response.
- Sentence segmentation (biomedical-aware tokenizer/segmenter recommended, e.g., scispaCy or similar, to avoid mis-splitting on abbreviations like "vs." or "p<0.05").
- Store both raw and normalized text per abstract for traceability.

### 4.3 Deduplication
- Use PMID as unique key to prevent reprocessing/duplicate storage of the same abstract on repeated queries.

---

## 5. Database Schema (SQLite)

**Table: `abstracts`**

| Column | Type | Notes |
|---|---|---|
| abstract_id | TEXT PRIMARY KEY | PMID |
| title | TEXT | |
| raw_text | TEXT | |
| normalized_text | TEXT | |
| source_query | TEXT | |
| retrieved_at | TIMESTAMP | |

**Table: `entities`**

| Column | Type | Notes |
|---|---|---|
| entity_id | INTEGER PK AUTOINCREMENT | |
| abstract_id | TEXT | FK → abstracts(abstract_id) |
| entity_type | TEXT | Disease \| Drug \| SampleSize \| Endpoint |
| text_span | TEXT | |
| char_start | INTEGER | |
| char_end | INTEGER | |
| confidence_score | REAL | |

**Table: `relations`**

| Column | Type | Notes |
|---|---|---|
| relation_id | INTEGER PK AUTOINCREMENT | |
| abstract_id | TEXT | FK → abstracts(abstract_id) |
| subject_entity_id | INTEGER | FK → entities(entity_id) |
| object_entity_id | INTEGER | FK → entities(entity_id) |
| relation_type | TEXT | Drug→Disease \| Drug→Cohort \| Outcome |
| confidence_score | REAL | |

**Table: `assertions`**

| Column | Type | Notes |
|---|---|---|
| assertion_id | INTEGER PK AUTOINCREMENT | |
| relation_id | INTEGER | FK → relations(relation_id) |
| assertion_type | TEXT | Positive \| Negated \| Conditional |
| confidence_score | REAL | |

**Table: `review_log`**

| Column | Type | Notes |
|---|---|---|
| review_id | INTEGER PK AUTOINCREMENT | |
| target_table | TEXT | 'entities' \| 'relations' \| 'assertions' |
| target_id | INTEGER | |
| reviewer_status | TEXT | unreviewed \| approved \| corrected \| rejected |
| corrected_value | TEXT | nullable |
| reviewed_by | TEXT | |
| reviewed_at | TIMESTAMP | |

**Indices:**
- `entities(abstract_id)`
- `relations(abstract_id)`, `relations(subject_entity_id)`, `relations(object_entity_id)`
- `assertions(relation_id)`
- `review_log(target_table, target_id)`

---

## 6. API Layer (Backend ↔ Dashboard)

Recommended REST endpoints (framework-agnostic):

**`POST /api/ingest`**
- Body: `{ query: string }`
- Triggers PubMed search + fetch + pipeline run on results.
- Returns: list of `abstract_id`s processed.

**`GET /api/abstracts/{abstract_id}`**
- Returns raw text, extracted entities, relations, assertions with confidence scores, for inline highlighting.

**`GET /api/search`**
- Query params: `drug`, `disease`, `assertion_type`, `min_confidence`, etc.
- Returns filtered set of relation/assertion records joined with entity text and source abstract reference.

**`GET /api/export`**
- Query params: same as `/api/search`.
- Returns CSV or JSON of matching records.

**`POST /api/review`**
- Body: `{ target_table, target_id, status, corrected_value?, reviewed_by }`
- Writes a row to `review_log` and updates confidence/trust flag on the target record.

**`GET /api/evaluation`**
- Returns latest confusion matrix + per-class and macro-averaged Precision/Recall/F1 for NER, RE, and AD (from the evaluation harness, Section 7).

---

## 7. Evaluation Harness

### 7.1 Process
1. Load gold-standard annotated test split.
2. Run the pipeline on the same raw abstracts (not previously seen during training).
3. Align predicted spans/relations/assertions to gold labels (use IoU/exact-span-match rules for NER; exact entity-pair + type match for RE; label match on aligned relations for AD).
4. Build confusion matrices per task.
5. Compute per-class Precision, Recall, F1, and macro-averages across classes.
6. Persist evaluation run results (versioned) for tracking improvement over milestones (Core NLP → Integrated System → Complete App → Final Project).

### 7.2 Metrics to Report
- **NER:** per-entity-type P/R/F1 + macro-average.
- **RE:** per-relation-type P/R/F1 + macro-average.
- **AD:** per-assertion-class (Positive/Negated/Conditional) P/R/F1 + macro-average.
- Optional: end-to-end pipeline accuracy (entity correct AND relation correct AND assertion correct, chained).

---

## 8. Non-Functional / Engineering Requirements

| Category | Requirement |
|---|---|
| Performance | Single-abstract inference target of a few seconds on available hardware (CPU acceptable for demo scale; GPU preferred for batch-processing many abstracts). |
| Reproducibility | Fix random seeds for train/test splits and model training runs used in reported metrics. |
| Traceability | Every stored entity/relation/assertion must be traceable back to `abstract_id` and exact character span. |
| Data integrity | Foreign key constraints enforced between entities, relations, and assertions tables. |
| Portability | SQLite file should be a single portable artifact for demo/handoff; no external DB server dependency. |
| Extensibility | Schema and API should allow adding new entity or relation types without breaking existing records (e.g., avoid hardcoding type lists in application logic beyond a lookup table). |

---

## 9. Tech Stack (Recommended)

- **Model/NLP:** Python, HuggingFace Transformers (biomedical pretrained encoder, e.g., BioBERT/PubMedBERT-class model), PyTorch.
- **Ingestion:** Python (`requests`/`httpx`) against NCBI E-utilities.
- **Backend/API:** Python (FastAPI or Flask) serving REST endpoints.
- **Database:** SQLite (via SQLAlchemy or direct `sqlite3`).
- **Frontend:** React (per product PRD / separate UI PRD).
- **Evaluation:** scikit-learn (`classification_report`, `confusion_matrix`) or custom scorer for span-level NER matching.

---

## 10. Risks (Technical)

- Span alignment ambiguity between model tokenization and gold annotation character offsets — needs a consistent tokenizer/offset-mapping strategy.
- Multi-task loss balancing may require experimentation; document final weighting scheme used.
- NCBI API availability/rate limiting could bottleneck live ingestion demos — consider a cached fallback set of abstracts for the live demo.
- SQLite write concurrency is limited — fine for a single reviewer, but simultaneous multi-user review sessions may need to be serialized or migrated to Postgres in future.
