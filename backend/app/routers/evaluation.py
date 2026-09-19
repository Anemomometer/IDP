import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..evaluation_service import EvaluationHarness
from ..models_db import EvaluationRun

router = APIRouter(prefix="/api/evaluation", tags=["Evaluation Dashboard"])
harness = EvaluationHarness()

@router.get("", response_model=list[dict])
def list_evaluation_runs(limit: int = 10, db: Session = Depends(get_db)):
    """
    Lists versioned evaluation runs stored in SQLite.
    """
    runs = db.query(EvaluationRun).order_by(EvaluationRun.run_timestamp.desc()).limit(limit).all()
    out = []
    for r in runs:
        out.append({
            "run_id": r.run_id,
            "task": r.task,
            "run_timestamp": r.run_timestamp.isoformat(),
            "dataset_version": r.dataset_version,
            "metrics": json.loads(r.metrics_json) if r.metrics_json else {},
            "confusion_matrix": json.loads(r.confusion_matrix_json) if r.confusion_matrix_json else {}
        })
    return out

@router.get("/latest")
def get_latest_evaluation(db: Session = Depends(get_db)):
    """
    Returns the most recent evaluation run metrics.
    """
    latest = db.query(EvaluationRun).order_by(EvaluationRun.run_timestamp.desc()).first()
    if not latest:
        # Run initial evaluation automatically if none exists
        res = harness.run_evaluation(db=db, task="ALL", dataset_version="v1.0-gold")
        return res

    return {
        "run_id": latest.run_id,
        "task": latest.task,
        "run_timestamp": latest.run_timestamp.isoformat(),
        "dataset_version": latest.dataset_version,
        "metrics": json.loads(latest.metrics_json) if latest.metrics_json else {},
        "confusion_matrix": json.loads(latest.confusion_matrix_json) if latest.confusion_matrix_json else {}
    }

@router.post("/run")
def trigger_evaluation_run(task: str = "ALL", dataset_version: str = "v1.0-gold", db: Session = Depends(get_db)):
    """
    Triggers a new evaluation harness run against gold_standard.json and persists results.
    """
    res = harness.run_evaluation(db=db, task=task, dataset_version=dataset_version)
    return res
