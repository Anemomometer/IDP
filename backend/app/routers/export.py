import csv
import io
import json

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session, aliased

from ..database import get_db
from ..models_db import Abstract, Assertion, Entity, Relation

router = APIRouter(prefix="/api/export", tags=["Export"])

@router.get("")
def export_evidence(
    format: str = Query("csv", pattern="^(csv|json)$"),
    drug: str | None = Query(None),
    disease: str | None = Query(None),
    relation_type: str | None = Query(None),
    assertion_type: str | None = Query(None),
    min_confidence: float = Query(0.0, ge=0.0, le=1.0),
    review_status: str | None = Query(None),
    db: Session = Depends(get_db)
):
    """
    Exports filtered evidence records as CSV or JSON matching active search criteria.
    """
    SubjEntity = aliased(Entity, name="subj_entity")
    ObjEntity = aliased(Entity, name="obj_entity")

    query = db.query(
        Relation,
        Abstract.title.label("abstract_title"),
        SubjEntity.text_span.label("subject_text"),
        SubjEntity.entity_type.label("subject_type"),
        ObjEntity.text_span.label("object_text"),
        ObjEntity.entity_type.label("object_type"),
        Assertion.assertion_type.label("assertion_type")
    ).join(
        Abstract, Relation.abstract_id == Abstract.abstract_id
    ).join(
        SubjEntity, Relation.subject_entity_id == SubjEntity.entity_id
    ).join(
        ObjEntity, Relation.object_entity_id == ObjEntity.entity_id
    ).outerjoin(
        Assertion, Relation.relation_id == Assertion.relation_id
    )

    if drug:
        query = query.filter((SubjEntity.text_span.ilike(f"%{drug}%")) | (ObjEntity.text_span.ilike(f"%{drug}%")))
    if disease:
        query = query.filter((SubjEntity.text_span.ilike(f"%{disease}%")) | (ObjEntity.text_span.ilike(f"%{disease}%")))
    if relation_type:
        query = query.filter(Relation.relation_type == relation_type)
    if assertion_type:
        query = query.filter(Assertion.assertion_type == assertion_type)
    if min_confidence > 0.0:
        query = query.filter(Relation.confidence_score >= min_confidence)
    if review_status:
        query = query.filter(Relation.review_status == review_status)

    results = query.all()

    export_records = []
    for row in results:
        rel = row[0]
        export_records.append({
            "relation_id": rel.relation_id,
            "pmid": rel.abstract_id,
            "abstract_title": row.abstract_title,
            "subject_text": row.subject_text,
            "subject_type": row.subject_type,
            "relation_type": rel.relation_type,
            "object_text": row.object_text,
            "object_type": row.object_type,
            "assertion_type": row.assertion_type or "Positive",
            "confidence_score": rel.confidence_score,
            "extraction_method": rel.extraction_method,
            "review_status": rel.review_status
        })

    if format == "json":
        json_content = json.dumps(export_records, indent=2)
        return Response(
            content=json_content,
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=clinical_evidence_export.json"}
        )

    # Default CSV Export
    output = io.StringIO()
    fieldnames = [
        "relation_id", "pmid", "abstract_title", "subject_text", "subject_type",
        "relation_type", "object_text", "object_type", "assertion_type",
        "confidence_score", "extraction_method", "review_status"
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(export_records)

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=clinical_evidence_export.csv"}
    )
