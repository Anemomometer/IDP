# Data Directory & Gold-Standard Benchmark Set

## Benchmark Dataset (`gold_standard.json`)
The `gold_standard.json` file contains 15 real clinical trial PubMed abstracts retrieved live from the NCBI PubMed API on a representative query (`pembrolizumab melanoma clinical trial`).

### Schema
Each record in `gold_standard.json` has the following structure:
```json
{
  "pmid": "42692071",
  "title": "Article Title...",
  "raw_text": "Full abstract text...",
  "normalized_text": "Normalized abstract text...",
  "gold_entities": [],
  "gold_relations": [],
  "gold_assertions": [],
  "status": "UNANNOTATED_STUB"
}
```

### Hand-Annotation Notice
> [!IMPORTANT]
> The `gold_entities`, `gold_relations`, and `gold_assertions` arrays are intentionally left empty (`[]`) for human review. No synthetic or model-generated labels are injected here.
> 
> - **Human Review Workflow:** Domain experts can fill in ground-truth entity spans, relation pairs, and assertion labels directly in `gold_standard.json` or via the **Review Queue UI** in the dashboard.
> - **Evaluation Harness Behavior:** The evaluation harness (`backend/app/evaluation_service.py`) executes cleanly against `gold_standard.json` regardless of label density. If unannotated stubs are evaluated, scores will reflect zero true positives until hand-annotations are saved.

## Database File (`evidence.db`)
The SQLite database stores all ingested PubMed abstracts, extracted entities, relations, assertions, human review logs, and versioned evaluation runs.
