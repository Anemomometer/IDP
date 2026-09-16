from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models_db import Abstract, Entity, Relation, Assertion
from ..schemas import IngestRequest, IngestResponse
from ..pubmed_service import PubMedClient, PubMedAPIError, PubMedRateLimitError
from ..nlp_service import RuleNLPProcessor

router = APIRouter(prefix="/api/ingest", tags=["Ingestion"])
pubmed_client = PubMedClient()
nlp_processor = RuleNLPProcessor()

@router.post("", response_model=IngestResponse)
def ingest_abstracts(payload: IngestRequest, db: Session = Depends(get_db)):
    """
    Triggers PubMed fetch + NLP pipeline execution and stores extracted evidence in SQLite.
    """
    if not payload.query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty.")

    try:
        pmids = pubmed_client.search(payload.query, max_results=payload.max_results)
    except PubMedRateLimitError as err:
        raise HTTPException(status_code=429, detail=str(err))
    except PubMedAPIError as err:
        raise HTTPException(status_code=502, detail=str(err))

    if not pmids:
        return IngestResponse(
            query=payload.query,
            total_fetched=0,
            abstract_ids=[],
            new_count=0,
            existing_count=0,
            message="No PubMed abstracts matched your query."
        )

    # Fetch full abstract XML/text
    try:
        abstract_items = pubmed_client.fetch_abstracts(pmids)
    except PubMedRateLimitError as err:
        raise HTTPException(status_code=429, detail=str(err))
    except PubMedAPIError as err:
        raise HTTPException(status_code=502, detail=str(err))

    processed_ids = []
    new_count = 0
    existing_count = 0

    for item in abstract_items:
        pmid = item["abstract_id"]
        processed_ids.append(pmid)

        # Check if already exists in DB
        existing = db.query(Abstract).filter(Abstract.abstract_id == pmid).first()
        if existing:
            existing_count += 1
            continue

        # Create Abstract record
        abs_record = Abstract(
            abstract_id=pmid,
            title=item["title"],
            raw_text=item["raw_text"],
            normalized_text=item["normalized_text"],
            source_query=payload.query
        )
        db.add(abs_record)
        db.flush() # Flush to make abs_record active

        # Run NLP Processor
        extraction = nlp_processor.process_abstract(item["normalized_text"], extraction_method="rule_based")

        # Map entity_id temp integer to DB ORM Entity objects
        temp_to_db_entity = {}
        for ent_data in extraction["entities"]:
            db_ent = Entity(
                abstract_id=pmid,
                entity_type=ent_data["entity_type"],
                text_span=ent_data["text_span"],
                char_start=ent_data["char_start"],
                char_end=ent_data["char_end"],
                confidence_score=ent_data["confidence_score"],
                extraction_method=ent_data["extraction_method"],
                review_status="unreviewed"
            )
            db.add(db_ent)
            db.flush()
            temp_to_db_entity[ent_data["entity_id"]] = db_ent.entity_id

        # Create Relations and Assertions
        for rel_data in extraction["relations"]:
            subj_id = temp_to_db_entity.get(rel_data["subject_entity_id"])
            obj_id = temp_to_db_entity.get(rel_data["object_entity_id"])
            if not subj_id or not obj_id:
                continue

            db_rel = Relation(
                abstract_id=pmid,
                subject_entity_id=subj_id,
                object_entity_id=obj_id,
                relation_type=rel_data["relation_type"],
                confidence_score=rel_data["confidence_score"],
                extraction_method=rel_data["extraction_method"],
                review_status="unreviewed"
            )
            db.add(db_rel)
            db.flush()

            # Find matching assertions for this relation
            matching_assertions = [a for a in extraction["assertions"] if a["relation_id"] == rel_data["relation_id"]]
            for ass_data in matching_assertions:
                db_ass = Assertion(
                    relation_id=db_rel.relation_id,
                    assertion_type=ass_data["assertion_type"],
                    confidence_score=ass_data["confidence_score"],
                    extraction_method=ass_data["extraction_method"],
                    review_status="unreviewed"
                )
                db.add(db_ass)

        new_count += 1

    db.commit()

    return IngestResponse(
        query=payload.query,
        total_fetched=len(abstract_items),
        abstract_ids=processed_ids,
        new_count=new_count,
        existing_count=existing_count,
        message=f"Ingested {new_count} new abstracts ({existing_count} already in database)."
    )
