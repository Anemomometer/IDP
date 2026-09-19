from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models_db import Abstract, Assertion, Entity, Relation, ReviewLog
from ..schemas import ReviewRequest, ReviewResponse

router = APIRouter(prefix="/api/review", tags=["Human-in-the-Loop Review"])

@router.post("", response_model=ReviewResponse)
def submit_review(payload: ReviewRequest, db: Session = Depends(get_db)):
    """
    Writes a review action (Approve / Correct / Reject) to review_log and updates target entity/relation/assertion.
    """
    valid_tables = ["entities", "relations", "assertions"]
    if payload.target_table not in valid_tables:
        raise HTTPException(status_code=400, detail=f"Invalid target_table. Must be one of {valid_tables}")

    valid_statuses = ["approved", "corrected", "rejected"]
    if payload.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {valid_statuses}")

    # 1. Update target table record
    if payload.target_table == "entities":
        record = db.query(Entity).filter(Entity.entity_id == payload.target_id).first()
        if not record:
            raise HTTPException(status_code=404, detail=f"Entity ID {payload.target_id} not found.")
        record.review_status = payload.status
        if payload.status == "corrected" and payload.corrected_value:
            record.entity_type = payload.corrected_value

    elif payload.target_table == "relations":
        record = db.query(Relation).filter(Relation.relation_id == payload.target_id).first()
        if not record:
            raise HTTPException(status_code=404, detail=f"Relation ID {payload.target_id} not found.")
        record.review_status = payload.status
        if payload.status == "corrected" and payload.corrected_value:
            record.relation_type = payload.corrected_value

    elif payload.target_table == "assertions":
        record = db.query(Assertion).filter(Assertion.assertion_id == payload.target_id).first()
        if not record:
            raise HTTPException(status_code=404, detail=f"Assertion ID {payload.target_id} not found.")
        record.review_status = payload.status
        if payload.status == "corrected" and payload.corrected_value:
            record.assertion_type = payload.corrected_value

    # 2. Write review log row
    log_entry = ReviewLog(
        target_table=payload.target_table,
        target_id=payload.target_id,
        reviewer_status=payload.status,
        corrected_value=payload.corrected_value,
        reviewed_by=payload.reviewed_by,
        reviewed_at=datetime.utcnow()
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)

    return ReviewResponse(
        review_id=log_entry.review_id,
        target_table=log_entry.target_table,
        target_id=log_entry.target_id,
        status=log_entry.reviewer_status,
        updated_at=log_entry.reviewed_at
    )

@router.get("/queue", response_model=list[dict])
def get_review_queue(limit: int = 50, db: Session = Depends(get_db)):
    """
    Surfaces unreviewed relations sorted by lowest confidence first for Screen 5 Review Queue.
    """
    unreviewed_relations = db.query(Relation).filter(
        Relation.review_status == "unreviewed"
    ).order_by(Relation.confidence_score.asc()).limit(limit).all()

    queue_items = []
    for rel in unreviewed_relations:
        abs_rec = db.query(Abstract).filter(Abstract.abstract_id == rel.abstract_id).first()
        subj = db.query(Entity).filter(Entity.entity_id == rel.subject_entity_id).first()
        obj = db.query(Entity).filter(Entity.entity_id == rel.object_entity_id).first()
        ass = db.query(Assertion).filter(Assertion.relation_id == rel.relation_id).first()

        queue_items.append({
            "relation_id": rel.relation_id,
            "abstract_id": rel.abstract_id,
            "abstract_title": abs_rec.title if abs_rec else "",
            "raw_text_snippet": abs_rec.normalized_text[:200] + "..." if abs_rec else "",
            "subject_text": subj.text_span if subj else "",
            "subject_type": subj.entity_type if subj else "",
            "relation_type": rel.relation_type,
            "object_text": obj.text_span if obj else "",
            "object_type": obj.entity_type if obj else "",
            "assertion_type": ass.assertion_type if ass else "Positive",
            "confidence_score": rel.confidence_score,
            "extraction_method": rel.extraction_method,
            "review_status": rel.review_status
        })

    return queue_items

@router.post("/bulk-approve")
def bulk_approve(min_confidence: float = 0.85, db: Session = Depends(get_db)):
    """
    Bulk approves all unreviewed relations with confidence score >= min_confidence threshold.
    """
    targets = db.query(Relation).filter(
        Relation.review_status == "unreviewed",
        Relation.confidence_score >= min_confidence
    ).all()

    approved_count = 0
    for rel in targets:
        rel.review_status = "approved"
        db.add(ReviewLog(
            target_table="relations",
            target_id=rel.relation_id,
            reviewer_status="approved",
            corrected_value=None,
            reviewed_by="bulk_action",
            reviewed_at=datetime.utcnow()
        ))
        approved_count += 1

    db.commit()
    return {"message": f"Successfully bulk-approved {approved_count} extractions.", "count": approved_count}
