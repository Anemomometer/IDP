
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models_db import Abstract, Entity, Relation
from ..schemas import (
    AbstractDetailResponse,
    EntitySchema,
    RelationSchema,
)

router = APIRouter(prefix="/api/abstracts", tags=["Abstracts"])

@router.get("", response_model=list[dict])
def list_abstracts(limit: int = 20, db: Session = Depends(get_db)):
    """
    Returns a list of recent ingested abstracts.
    """
    results = db.query(Abstract).order_by(Abstract.retrieved_at.desc()).limit(limit).all()
    out = []
    for a in results:
        out.append({
            "abstract_id": a.abstract_id,
            "title": a.title,
            "source_query": a.source_query,
            "retrieved_at": a.retrieved_at.isoformat() if a.retrieved_at else None,
            "entity_count": len(a.entities),
            "relation_count": len(a.relations)
        })
    return out

@router.get("/{abstract_id}", response_model=AbstractDetailResponse)
def get_abstract_detail(abstract_id: str, db: Session = Depends(get_db)):
    """
    Returns full abstract text, entities, relations, and assertions for inline highlighting.
    """
    abs_rec = db.query(Abstract).filter(Abstract.abstract_id == abstract_id).first()
    if not abs_rec:
        raise HTTPException(status_code=404, detail=f"Abstract PMID {abstract_id} not found.")

    entities = db.query(Entity).filter(Entity.abstract_id == abstract_id).all()
    relations = db.query(Relation).filter(Relation.abstract_id == abstract_id).options(
        joinedload(Relation.subject_entity),
        joinedload(Relation.object_entity),
        joinedload(Relation.assertions)
    ).all()

    return AbstractDetailResponse(
        abstract_id=abs_rec.abstract_id,
        title=abs_rec.title,
        raw_text=abs_rec.raw_text,
        normalized_text=abs_rec.normalized_text,
        source_query=abs_rec.source_query,
        retrieved_at=abs_rec.retrieved_at,
        entities=[EntitySchema.from_orm(e) for e in entities],
        relations=[RelationSchema.from_orm(r) for r in relations]
    )
