# Product Requirements Document (PRD)
## Clinical Trial NLP: Automated Information Extraction from Clinical Trial Literature

**Reference Patent:** US20250252261A1
**Document Type:** Team Project — Product Requirements Document
**Version:** 1.0
**Status:** Draft

---

## 1. Executive Summary

Clinical Trial NLP is a system that automatically converts unstructured PubMed abstracts into structured, queryable evidence. A single shared biomedical language model performs three linked tasks — Named Entity Recognition (NER), Relation Extraction (RE), and Assertion Detection (AD) — on each abstract. Results are written to a SQLite database with confidence scores and surfaced through an analytics dashboard with human-in-the-loop review, so a researcher can go from "raw abstract" to "verified, structured evidence" without manual tagging.

---

## 2. Problem Statement

Clinical trial literature is difficult to use at scale for three reasons:

| # | Problem | Description |
|---|---------|-------------|
| 1 | **Unstructured text** | Key facts — disease, drug, sample size, endpoints, outcomes — are buried inside dense abstract prose rather than stored as discrete fields. |
| 2 | **Doesn't scale** | Manual tagging by researchers is slow and cannot keep pace with the volume of new PubMed publications. |
| 3 | **Context gets lost** | Simple keyword search cannot distinguish a drug that *treats* a disease from a finding that is *negated* or *conditional* — it treats every mention as equally positive. |

**Goal:** Build a pipeline that reads raw PubMed abstracts and outputs structured, assertion-aware evidence records that can be trusted, searched, and verified by a human reviewer.

---

## 3. Objectives & Success Criteria

### 3.1 Objectives
- Automatically extract clinically relevant entities from abstract text.
- Identify relationships between those entities (e.g., Drug → Disease, Drug → Cohort, Outcome links).
- Classify each extracted finding by assertion status: **positive**, **negated**, or **conditional**.
- Store every extraction with a confidence score in a structured, queryable database.
- Allow a human reviewer to verify or correct extractions before they are treated as trusted evidence.
- Ingest abstracts live from the NCBI PubMed API rather than relying on a static dataset.

### 3.2 Success Criteria
- Per-class and macro-averaged **Precision, Recall, and F1** reported for each of the three tasks (NER, RE, AD) against a hand-annotated gold-standard test split.
- A working end-to-end pipeline: PubMed query → extraction → database → dashboard.
- A functional review interface where a human can accept/reject/correct extractions with visible confidence scores.
- Exportable, filterable evidence tables from the dashboard.

---

## 4. Scope

### 4.1 In Scope
- Ingestion of abstracts via the NCBI PubMed API (live, on-demand or scheduled).
- A shared encoder architecture performing NER, RE, and Assertion Detection.
- Entity types covering at minimum: **DISEASE, DRUG, SAMPLE_SIZE, ENDPOINT**.
- Relation types covering at minimum: **TREATS, TESTED_IN, MEASURED_BY**.
- Assertion classification: **PRESENT_POSITIVE / ABSENT_NEGATED / CONDITIONAL**.
- Persistence layer: SQLite database with a defined schema for entities, relations, assertions, and confidence scores.
- React-based analytics dashboard with:
  - Color-coded inline text highlighting of extracted entities/relations.
  - Relation view.
  - Database search and filter.
  - Export functionality.
  - Human-in-the-loop review/correction workflow.
- Evaluation harness: gold-standard annotation, held-out test split, confusion matrix, P/R/F1 scoring.

### 4.2 Out of Scope (for this project phase)
- Full-text article parsing (PDFs, tables, figures) — abstracts only.
- Multi-language support (English abstracts only, assumed).
- Production-grade scaling/distributed database (SQLite is a deliberate lightweight choice, not a production DB).
- Automated clinical decision-making — outputs are evidence artifacts for human review, not a diagnostic tool.
- Real-time streaming ingestion (batch/pull-based ingestion from PubMed API is sufficient).

---

## 5. Proposed Solution / System Architecture

**Pipeline flow:**

```
PubMed Abstract (via NCBI API)
        │
        ▼
Shared Biomedical Language Model (single encoder)
        │
   ┌────┼────────────────┐
   ▼    ▼                ▼
 NER   Relation        Assertion
       Extraction      Detection
   │    │                │
   └────┴────────────────┘
              │
              ▼
   SQLite Database (entities, relations,
   assertions + confidence scores)
              │
              ▼
   Analytics Dashboard (React) +
   Human-in-the-Loop Review
```

### 5.1 Core Design Decision: Shared Encoder
Instead of training three separate models, one encoder is shared across NER, Relation Extraction, and Assertion Detection. Rationale:
- Faster to train and run than three independent pipelines.
- Each task benefits from shared biomedical language context learned by the encoder.
- Reduces total model footprint and inference cost.

### 5.2 Live PubMed Ingestion
- The system pulls directly from the **NCBI PubMed API**, rather than a fixed/static snapshot of abstracts.
- This means the evidence base can grow continuously as new literature is published, rather than degrading in relevance over time.

### 5.3 Assertion-Aware Extraction
- A key differentiator from typical clinical-text pipelines: most extractors treat every mention of a relationship as a positive/true finding.
- This system explicitly classifies each finding as:
  - **PRESENT_POSITIVE** — the relation is affirmed in the text.
  - **ABSENT_NEGATED** — the text explicitly denies the relation (e.g., "no significant improvement was observed").
  - **CONDITIONAL** — the relation holds only under stated conditions (e.g., "only in patients with prior treatment failure").

### 5.4 Human-in-the-Loop Review
- Every extraction is presented with **color-coded inline highlighting** in the source abstract.
- A reviewer can verify or correct any extraction before it is persisted as "trusted" evidence.
- This is built into the core workflow from the start, not bolted on later — reflecting a design decision made explicitly during planning.

---

## 6. Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | System shall query the NCBI PubMed API and retrieve abstracts matching a search term or ID list. | Must |
| FR-2 | System shall run the shared encoder over each retrieved abstract to produce NER, RE, and AD outputs in a single pass. | Must |
| FR-3 | System shall extract entities of type DISEASE, DRUG, SAMPLE_SIZE, and ENDPOINT, each with a confidence score. | Must |
| FR-4 | System shall extract relations of type TREATS, TESTED_IN, and MEASURED_BY, each with a confidence score. | Must |
| FR-5 | System shall classify each extracted relation/finding as PRESENT_POSITIVE, ABSENT_NEGATED, or CONDITIONAL. | Must |
| FR-6 | System shall persist all extraction results (entities, relations, assertions, confidence scores, source abstract reference) into a SQLite database. | Must |
| FR-7 | System shall provide a dashboard view that highlights entities/relations inline within the source abstract text, color-coded by type/assertion. | Must |
| FR-8 | System shall provide a relation view showing extracted relationships independent of raw text. | Should |
| FR-9 | System shall allow the user to search and filter the database (e.g., by drug, disease, assertion type, confidence threshold). | Must |
| FR-10 | System shall allow export of query results/evidence tables (e.g., CSV/JSON). | Should |
| FR-11 | System shall allow a human reviewer to approve, reject, or edit any individual extraction, with the correction persisted back to the database. | Must |
| FR-12 | System shall support evaluation mode: scoring predictions against a hand-annotated gold-standard test split and producing a confusion matrix plus per-class and macro-averaged Precision, Recall, F1. | Must |

---

## 7. Non-Functional Requirements

| Category | Requirement |
|----------|-------------|
| **Performance** | Extraction pipeline should process a single abstract in near-real-time (target: a few seconds) to support interactive review. |
| **Scalability** | SQLite is acceptable at project scale (hundreds–low thousands of abstracts); architecture should not preclude a future swap to a heavier DB if evidence volume grows significantly. |
| **Usability** | Dashboard must be understandable to a non-ML clinical/research user — color coding and highlighting should be self-explanatory, with confidence scores visible. |
| **Reliability** | No extraction should be presented as "confirmed evidence" without either high model confidence or human verification. |
| **Portability** | SQLite chosen specifically for lightweight, file-based portability (no server setup required for evaluation/demo). |
| **Auditability** | Every stored record must retain traceability to its source abstract (e.g., PMID) and to whether it was human-reviewed. |

---

## 8. Data Model (Conceptual)

**Abstracts**
- `abstract_id` (PMID), `title`, `raw_text`, `retrieved_date`

**Entities**
- `entity_id`, `abstract_id` (FK), `entity_type` (DISEASE/DRUG/SAMPLE_SIZE/ENDPOINT), `text_span`, `char_start`, `char_end`, `confidence_score`

**Relations**
- `relation_id`, `abstract_id` (FK), `subject_entity_id` (FK), `object_entity_id` (FK), `relation_type` (TREATS / TESTED_IN / MEASURED_BY), `confidence_score`

**Assertions**
- `assertion_id`, `relation_id` (FK), `assertion_type` (PRESENT_POSITIVE/ABSENT_NEGATED/CONDITIONAL), `confidence_score`

**Review**
- `review_id`, `target_id` (entity/relation/assertion), `reviewer_status` (unreviewed/approved/corrected/rejected), `corrected_value` (nullable), `reviewed_by`, `reviewed_at`

*(Exact schema/columns to be finalized during the "Foundation" milestone — see Section 10.)*

---

## 9. Validation & Evaluation Methodology

1. **Gold-standard annotation** — Hand-annotate a subset of PubMed abstracts across entity, relation, and assertion labels.
2. **Held-out test split** — Reserve a portion of the gold-standard set purely for unbiased evaluation (not used in development/tuning).
3. **Scoring** — Score each task's predictions (NER, RE, AD) against gold labels using a confusion matrix.
4. **Reporting** — Report both per-class and macro-averaged Precision, Recall, and F1 for each task.

This same methodology should be re-run at the "Complete App" milestone (initial P/R/F1 evaluation) and finalized at "Final Project" (final evaluation).

---

## 10. Development Roadmap

| Milestone | % Complete | Deliverables |
|-----------|-----------|--------------|
| **Foundation** | 20% | Problem statement, patent study, benchmark abstracts collected, entity/relation/assertion schema defined, SQLite schema design. |
| **Core NLP** | 30% | NER, Relation Extraction, and Assertion Detection built and tested individually. |
| **Integrated System** | 50% | All 3 tasks combined into one shared-encoder pipeline; PubMed API integrated; basic React UI in place. |
| **Complete App** | 80% | Inline highlighting, relation view, DB search/filter, export, initial P/R/F1 evaluation. |
| **Final Project** | 100% | Full testing, final evaluation, written report, presentation deck, demo, and viva Q&A. |

---

## 11. Key Risks & Open Questions

| Risk / Question | Notes |
|---|---|
| Annotation bandwidth | Hand-annotating a sufficiently large gold-standard set is labor-intensive; scope of the annotated set should be fixed early. |
| Assertion detection difficulty | Negation/conditional detection is historically harder than plain NER — may need dedicated attention/tuning in the "Core NLP" phase. |
| Shared encoder trade-offs | Multi-task shared encoders can underperform single-task models on any one task if not balanced carefully during training — worth monitoring per-task metrics, not just aggregate. |
| PubMed API rate limits | Live ingestion should respect NCBI API usage/rate-limit policies. |
| SQLite concurrency | Fine for single-user demo use; would need revisiting if multiple reviewers use the dashboard concurrently. |
| Definition of "Sample Size" / "Endpoint" entities | These are less standardized than Disease/Drug — schema should pin down exact extraction boundaries during Foundation phase. |

---

## 12. Out-of-the-Box Differentiators (Summary)

1. **One Model, Three Tasks** — single shared encoder for NER + RE + Assertion Detection, not three separate pipelines.
2. **Live PubMed Ingestion** — evidence base grows with the literature rather than being a static snapshot.
3. **Assertion-Aware Extraction** — explicitly distinguishes positive, negated, and conditional findings, which most extractors miss.
4. **Human-in-the-Loop by Design** — review and correction is a first-class part of the workflow, not an afterthought.

---

*Prepared as a supporting PRD for the "Clinical Trial NLP" team project (Patent reference: US20250252261A1).*
