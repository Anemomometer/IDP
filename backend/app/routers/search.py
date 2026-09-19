
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, aliased

from ..database import get_db
from ..models_db import Abstract, Assertion, Entity, Relation
from ..schemas import SearchItem, SearchResponse

router = APIRouter(prefix="/api/search", tags=["Search & Evidence Database"])

@router.get("", response_model=SearchResponse)
def search_evidence(
    drug: str | None = Query(None, description="Drug name query"),
    disease: str | None = Query(None, description="Disease name query"),
    relation_type: str | None = Query(None, description="Relation type (Drug→Disease, Drug→Cohort, Outcome-link)"),
    assertion_type: str | None = Query(None, description="Assertion type (Positive, Negated, Conditional)"),
    min_confidence: float = Query(0.0, ge=0.0, le=1.0, description="Minimum confidence threshold"),
    review_status: str | None = Query(None, description="Review status filter"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search and filter extracted evidence across the SQLite database with AND logic.
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

    # Apply AND filters
    if drug:
        query = query.filter(
            (SubjEntity.text_span.ilike(f"%{drug}%")) | (ObjEntity.text_span.ilike(f"%{drug}%"))
        )
    if disease:
        query = query.filter(
            (SubjEntity.text_span.ilike(f"%{disease}%")) | (ObjEntity.text_span.ilike(f"%{disease}%"))
        )
    if relation_type:
        query = query.filter(Relation.relation_type == relation_type)
    if assertion_type:
        query = query.filter(Assertion.assertion_type == assertion_type)
    if min_confidence > 0.0:
        query = query.filter(Relation.confidence_score >= min_confidence)
    if review_status:
        query = query.filter(Relation.review_status == review_status)

    total = query.count()
    offset = (page - 1) * page_size
    results = query.offset(offset).limit(page_size).all()

    items = []
    for row in results:
        rel = row[0]
        items.append(SearchItem(
            relation_id=rel.relation_id,
            abstract_id=rel.abstract_id,
            abstract_title=row.abstract_title,
            subject_text=row.subject_text,
            subject_type=row.subject_type,
            relation_type=rel.relation_type,
            object_text=row.object_text,
            object_type=row.object_type,
            assertion_type=row.assertion_type or "Positive",
            confidence_score=rel.confidence_score,
            extraction_method=rel.extraction_method,
            review_status=rel.review_status
        ))

    return SearchResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )
