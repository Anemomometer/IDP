# Clinical Trial NLP — Joint Multi-Task Biomedical NLP System & Review Dashboard

## Goal Description
Build a full-stack system ("Clinical Trial NLP") based on patent US20250252261A1 that:
1. Ingests PubMed abstracts live via NCBI E-utilities (`ESearch` + `EFetch`), normalizes text, and deduplicates by PMID.
2. Extracts structured evidence using a PyTorch shared-encoder model (BioBERT/PubMedBERT-class backbone) with 3 joint task heads:
   - **NER Head**: BIO tagging for DISEASE, DRUG, SAMPLE_SIZE, ENDPOINT.
   - **Relation Extraction Head**: classifies entity pairs into `TREATS`, `TESTED_IN`, `MEASURED_BY`.
   - **Assertion Detection Head**: classifies relations as `PRESENT_POSITIVE`, `ABSENT_NEGATED`, or `CONDITIONAL`.
3. Persists records with confidence scores into SQLite (`abstracts`, `entities`, `relations`, `assertions`, `review_log`).
4. Exposes REST API endpoints (`/api/ingest`, `/api/abstracts/{id}`, `/api/search`, `/api/export`, `/api/review`, `/api/evaluation`).
5. Provides a React UI with 6 distinct screens (Ingest/Search, Abstract Detail with color-blind-safe inline highlighting & popovers, Relation View, Evidence Database, Review Queue, Evaluation Dashboard).
6. Features a versioned Evaluation Harness scoring against a held-out gold-standard test set with span/pair match rules, producing per-class and macro P/R/F1 metrics and confusion matrices.

## User Review Required
> [!IMPORTANT]
> - **Pretrained Model Backbone**: We will use `microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext` (or fallback biomedical encoder) as the shared encoder. A hybrid neural + bio-aware rule-refined inference pipeline will ensure instant startup and robust extraction even in CPU environments.
> - **Gold-Standard Dataset**: A hand-annotated held-out benchmark split (`data/gold_standard.json`) covering representative PubMed clinical trial abstracts with known entities, relations, and assertions will be included to evaluate the harness independently of model training.

## Open Questions
None at this stage. All requirements, taxonomies, schemas, API contracts, UI screens, and build milestones are fully specified in the prompt and PRD documents.

## Proposed Changes

### Data Pipeline & NLP Core (`model/`, `data/`)
#### [NEW] [taxonomy.json](file:///d:/IDp/data/taxonomy.json)
- JSON mapping for entity types (`DISEASE`, `DRUG`, `SAMPLE_SIZE`, `ENDPOINT`), relation types (`TREATS`, `TESTED_IN`, `MEASURED_BY`), and assertion types (`PRESENT_POSITIVE`, `ABSENT_NEGATED`, `CONDITIONAL`).

#### [NEW] [gold_standard.json](file:///d:/IDp/data/gold_standard.json)
- Hand-annotated held-out test split of clinical abstracts with gold entity spans, relation pairs, and assertion labels.

#### [NEW] [encoder.py](file:///d:/IDp/model/encoder.py)
- `SharedBiomedicalEncoder` class inheriting from `torch.nn.Module`, wrapping PubMedBERT hidden representations.

#### [NEW] [heads.py](file:///d:/IDp/model/heads.py)
- `NERHead` (token-level linear classification with BIO mapping), `RelationExtractionHead` (pairwise entity hidden state classification), `AssertionDetectionHead` (span/context classification).

#### [NEW] [trainer.py](file:///d:/IDp/model/trainer.py)
- Multi-task loss computer combining cross-entropy losses for NER, RE, and AD with configurable per-task weights ($\lambda_{NER}, \lambda_{RE}, \lambda_{AD}$).

#### [NEW] [pipeline.py](file:///d:/IDp/model/pipeline.py)
- Joint inference wrapper `ClinicalNLPProcessor` taking raw text, sentence segmenting, computing token span offsets, running model heads, calculating confidence scores, and assembling entity/relation/assertion structures.

---

### Backend API & Database (`backend/`)
#### [NEW] [database.py](file:///d:/IDp/backend/app/database.py)
- SQLite database connection, SQLAlchemy session engine, foreign key enforcement (`PRAGMA foreign_keys = ON`), and table creation logic.

#### [NEW] [models_db.py](file:///d:/IDp/backend/app/models_db.py)
- SQLAlchemy ORM models matching schema: `Abstract`, `Entity`, `Relation`, `Assertion`, `ReviewLog`, `EvaluationRun`.

#### [NEW] [schemas.py](file:///d:/IDp/backend/app/schemas.py)
- Pydantic response and request models for ingestion, search, review, export, and evaluation.

#### [NEW] [pubmed_service.py](file:///d:/IDp/backend/app/pubmed_service.py)
- `PubMedClient` using `httpx`/`requests` to query NCBI E-utilities (`esearch.fcgi`, `efetch.fcgi`), parse PubMed XML, normalize text, and deduplicate PMIDs.

#### [NEW] [evaluation_service.py](file:///d:/IDp/backend/app/evaluation_service.py)
- Evaluation harness engine scoring NER via character span IoU/exact match, RE via entity pair match, and AD via label alignment against `gold_standard.json`. Generates confusion matrices and per-class + macro P/R/F1.

#### [NEW] [ingest.py](file:///d:/IDp/backend/app/routers/ingest.py)
- `POST /api/ingest` — Fetches PubMed abstracts, runs multi-task NLP, saves extractions to SQLite.

#### [NEW] [abstracts.py](file:///d:/IDp/backend/app/routers/abstracts.py)
- `GET /api/abstracts/{abstract_id}` — Returns abstract text, entities, relations, assertions, and review status for inline highlighting.

#### [NEW] [search.py](file:///d:/IDp/backend/app/routers/search.py)
- `GET /api/search` — Filter evidence records by drug, disease, relation_type, assertion_type, min_confidence, review_status with pagination.

#### [NEW] [export.py](file:///d:/IDp/backend/app/routers/export.py)
- `GET /api/export` — Export filtered evidence as CSV or JSON matching active search criteria.

#### [NEW] [review.py](file:///d:/IDp/backend/app/routers/review.py)
- `POST /api/review` — Log human corrections, update entity/relation/assertion status in DB.

#### [NEW] [evaluation.py](file:///d:/IDp/backend/app/routers/evaluation.py)
- `GET /api/evaluation` & `POST /api/evaluation/run` — Run evaluation harness and return versioned P/R/F1 metrics and confusion matrices.

#### [NEW] [main.py](file:///d:/IDp/backend/app/main.py)
- FastAPI entry point with CORS middleware, router registration, and startup database initialization.

---

### Frontend UI (`frontend/`)
#### [NEW] [package.json](file:///d:/IDp/frontend/package.json) & [vite.config.js](file:///d:/IDp/frontend/vite.config.js)
- Vite + React application setup with Lucide icons / custom SVG icons for color-blind safe encoding.

#### [NEW] [index.css](file:///d:/IDp/frontend/src/index.css)
- Comprehensive CSS styling with dark/teal clinical theme, accessible high-contrast colors, subtle highlight tints, assertion styles, and popover positioning.

#### [NEW] [App.jsx](file:///d:/IDp/frontend/src/App.jsx)
- Top navbar, active tab state, quick metrics summary, error/toast notification host.

#### [NEW] [IngestSearch.jsx](file:///d:/IDp/frontend/src/screens/IngestSearch.jsx)
- Screen 1: Query bar, "Fetch Abstracts" button with loading/error states, recent queries chips, result cards.

#### [NEW] [AbstractDetail.jsx](file:///d:/IDp/frontend/src/screens/AbstractDetail.jsx)
- Screen 2: Text renderer with character-accurate span highlights (DISEASE, DRUG, SAMPLE_SIZE, ENDPOINT), assertion overlays (PRESENT_POSITIVE = solid underline + check, ABSENT_NEGATED = strikethrough + red badge, CONDITIONAL = dashed + amber badge), hover popovers with numeric confidence, 3-click Approve/Correct/Reject actions, sidebar entity/relation list, always-visible legend.

#### [NEW] [RelationView.jsx](file:///d:/IDp/frontend/src/screens/RelationView.jsx)
- Screen 3: Table view of extracted entity pairs, assertion badges, confidence scores, relation filter chips; clicking row jumps to span in Abstract Detail.

#### [NEW] [EvidenceDatabase.jsx](file:///d:/IDp/frontend/src/screens/EvidenceDatabase.jsx)
- Screen 4: Full multi-filter panel (drug, disease, relation type, assertion type, confidence slider, review status with AND logic), active filter chips, paginated table, export CSV/JSON buttons.

#### [NEW] [ReviewQueue.jsx](file:///d:/IDp/frontend/src/screens/ReviewQueue.jsx)
- Screen 5: Queue sorted by lowest confidence first, Approve/Correct/Reject per item, progress counter, bulk-approve threshold action.

#### [NEW] [EvaluationDashboard.jsx](file:///d:/IDp/frontend/src/screens/EvaluationDashboard.jsx)
- Screen 6: Task tabs (NER, RE, AD), versioned evaluation run selector, interactive confusion matrix grid, per-class and macro P/R/F1 tables.

---

## Verification Plan

### Automated Tests
- `pytest` test suite verifying:
  - Database schema & foreign key constraints (`sqlite3` / `SQLAlchemy`).
  - PubMed API parser on XML sample fixtures.
  - Multi-task PyTorch model forward pass shapes for NER, RE, and AD heads.
  - Evaluation harness calculation of Precision, Recall, F1, and Confusion Matrix.
  - FastAPI endpoints (`/api/ingest`, `/api/abstracts/{id}`, `/api/search`, `/api/export`, `/api/review`, `/api/evaluation`).

### Manual Verification
- Execute `npm run dev` for Vite frontend and `uvicorn backend.app.main:app` for FastAPI backend.
- Run PubMed search for "pembrolizumab melanoma" on Screen 1, verify abstracts retrieved and extractions persisted to SQLite.
- Test inline text highlighting and popover actions on Screen 2. Verify correcting an extraction takes $\le 3$ clicks.
- Apply AND filters on Screen 4 and verify CSV export matches displayed table.
- Verify Evaluation Dashboard displays valid macro P/R/F1 scores from gold-standard evaluation.
