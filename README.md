# 🔬 Clinical Trial NLP: Automated Information Extraction & Evidence Discovery

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5.0-646CFF.svg)](https://vitejs.dev/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57.svg)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Reference Patent:** US20250252261A1  
> **Clinical Trial NLP** converts dense, unstructured PubMed clinical trial abstracts into structured, queryable evidence records using a unified biomedical NLP pipeline coupled with an interactive human-in-the-loop review dashboard.

---

## 📌 Problem Statement

Clinical trial literature expands rapidly, making manual data extraction slow, unscalable, and prone to context loss:
1. **Unstructured Prose**: Key trial findings (drug names, target diseases, sample sizes, endpoints, and trial outcomes) are buried inside unstructured abstracts.
2. **Context & Assertion Nuance**: Keyword search fails to distinguish between a drug that *effectively treats* a disease versus one where efficacy was *negated* or *conditional*.
3. **Manual Tagging Bottleneck**: Manual extraction cannot scale with the volume of daily NCBI PubMed publications.

---

## ✨ Key Features

- **Live PubMed Ingestion**: Search and fetch biomedical literature directly from the NCBI PubMed API.
- **Shared Biomedical Language Model Architecture**:
  - **Named Entity Recognition (NER)**: Identifies `DISEASE`, `DRUG`, `SAMPLE_SIZE`, and `ENDPOINT` entities.
  - **Relation Extraction (RE)**: Maps directed clinical links (`TREATS`, `TESTED_IN`, `MEASURED_BY`).
  - **Assertion Detection (AD)**: Classifies evidence modality into `PRESENT_POSITIVE`, `ABSENT_NEGATED`, or `CONDITIONAL`.
- **Confidence Scoring & Audit Trail**: Every entity, relation, and assertion is stored with model confidence metrics.
- **Interactive Review Dashboard**:
  - Color-coded entity highlighting and inline span visualization.
  - Graph & relation graph views.
  - Human-in-the-Loop review queue for approving, rejecting, or editing extractions.
  - Precision / Recall / F1 performance evaluation harness against benchmark datasets.
- **Evidence Database & Export**: Queryable SQLite storage with one-click JSON / CSV evidence export.

---

## 🏗️ Architecture

```mermaid
flowchart TD
    A[NCBI PubMed API] -->|Query & Fetch| B[FastAPI Ingestion Service]
    B --> C[Shared Biomedical Language Encoder]
    
    subgraph Multi-Task NLP Pipeline
        C --> D[NER Head\n(DISEASE, DRUG, SAMPLE_SIZE, ENDPOINT)]
        C --> E[Relation Extraction Head\n(TREATS, TESTED_IN, MEASURED_BY)]
        C --> F[Assertion Detection Head\n(PRESENT_POSITIVE, ABSENT_NEGATED, CONDITIONAL)]
    End

    D --> G[Confidence Scoring & Post-Processor]
    E --> G
    F --> G

    G --> H[(SQLite Evidence Database\nevidence.db)]
    
    H <--> I[FastAPI REST API]
    I <--> J[React + Vite Analytics Dashboard]
    J <--> K[Human-in-the-Loop Review Queue]
```

---

## 📂 Repository Structure

```
IDp/
├── backend/                  # FastAPI Backend Application
│   └── app/
│       ├── main.py           # FastAPI entrypoint & CORS middleware
│       ├── database.py       # SQLite connection & session management
│       ├── models_db.py     # SQLAlchemy ORM schemas
│       ├── schemas.py        # Pydantic data validation schemas
│       ├── pubmed_service.py # NCBI PubMed API fetcher & XML parser
│       ├── nlp_service.py    # Joint NER, RE, & Assertion pipeline engine
│       ├── evaluation_service.py # Metrics calculation harness (P/R/F1)
│       └── routers/          # API Route handlers (ingest, abstracts, search, review, evaluation, export)
│
├── frontend/                 # React + Vite Dashboard UI
│   ├── src/
│   │   ├── api/client.js     # Axios REST client API wrapper
│   │   ├── components/       # Header, Legend, Navigation components
│   │   └── screens/          # Ingest, Review Queue, Evidence DB, Evaluation Dashboard, Detail views
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── model/                    # ML Model & Training Pipelines
│   ├── encoder.py            # Shared transformer backbone encoder
│   ├── heads.py              # Multi-task classification heads (NER, RE, Assertion)
│   ├── pipeline.py           # Joint inference pipeline wrapper
│   └── trainer.py            # Multi-task loss trainer & evaluator
│
├── data/                     # Benchmark Data & Storage
│   ├── gold_standard.json    # Hand-annotated clinical trial benchmark set
│   ├── taxonomy.json         # Entity, relation, and assertion taxonomies
│   └── evidence.db           # SQLite database store
│
├── Clinical_Trial_NLP_PRD.md # Product Requirements Document
├── Clinical_Trial_NLP_Technical_PRD.md # Technical Architecture PRD
├── Clinical_Trial_NLP_UI_PRD.md        # UI/UX Specification PRD
├── implementation_plan.md    # Multi-phase implementation roadmap
└── .gitignore
```

---

## 🚀 Quickstart Guide

### Prerequisites
- **Python**: 3.10 or higher
- **Node.js**: v18 or higher (npm v9+)

---

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment (optional but recommended)
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install requirements (if requirements.txt is created) or required dependencies
pip install fastapi uvicorn sqlalchemy pydantic requests torch transformers

# Start FastAPI dev server
uvicorn app.main:app --reload --port 8000
```
*API docs available at: `http://localhost:8000/docs`*

---

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Start Vite development server
npm run dev
```
*Frontend application available at: `http://localhost:5173`*

---

## 📊 Evaluation & Benchmark Dataset

The system includes a gold-standard evaluation harness located in `data/gold_standard.json` and executed via `backend/app/evaluation_service.py`.

Metrics measured across held-out splits:
- **NER Metrics**: Span-level Micro and Macro Precision, Recall, and F1.
- **Relation Metrics**: Pairwise extraction accuracy and relation classification F1.
- **Assertion Metrics**: Confusion matrices across `PRESENT_POSITIVE`, `ABSENT_NEGATED`, and `CONDITIONAL` classes.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 📬 Contact & Patent Notice

Developed under reference patent **US20250252261A1** (*Automated Information Extraction from Clinical Trial Literature*).
