from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# --- Ingestion ---
class IngestRequest(BaseModel):
    query: str = Field(..., example="pembrolizumab melanoma")
    max_results: int = Field(default=10, ge=1, le=50)

class IngestResponse(BaseModel):
    query: str
    total_fetched: int
    abstract_ids: list[str]
    new_count: int
    existing_count: int
    message: str

# --- Entities / Relations / Assertions ---
class EntitySchema(BaseModel):
    entity_id: int
    abstract_id: str
    entity_type: str
    text_span: str
    char_start: int
    char_end: int
    confidence_score: float
    extraction_method: str = "model"
    review_status: str = "unreviewed"

    class Config:
        from_attributes = True

class AssertionSchema(BaseModel):
    assertion_id: int
    relation_id: int
    assertion_type: str
    confidence_score: float
    extraction_method: str = "model"
    review_status: str = "unreviewed"

    class Config:
        from_attributes = True

class RelationSchema(BaseModel):
    relation_id: int
    abstract_id: str
    subject_entity_id: int
    object_entity_id: int
    relation_type: str
    confidence_score: float
    extraction_method: str = "model"
    review_status: str = "unreviewed"
    subject_entity: EntitySchema | None = None
    object_entity: EntitySchema | None = None
    assertions: list[AssertionSchema] = []

    class Config:
        from_attributes = True

class AbstractDetailResponse(BaseModel):
    abstract_id: str
    title: str
    raw_text: str
    normalized_text: str
    source_query: str | None = None
    retrieved_at: datetime | None = None
    entities: list[EntitySchema] = []
    relations: list[RelationSchema] = []

    class Config:
        from_attributes = True

# --- Search ---
class SearchItem(BaseModel):
    relation_id: int
    abstract_id: str
    abstract_title: str
    subject_text: str
    subject_type: str
    relation_type: str
    object_text: str
    object_type: str
    assertion_type: str
    confidence_score: float
    extraction_method: str
    review_status: str

class SearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[SearchItem]

# --- Review ---
class ReviewRequest(BaseModel):
    target_table: str = Field(..., description="'entities' | 'relations' | 'assertions'")
    target_id: int
    status: str = Field(..., description="'approved' | 'corrected' | 'rejected'")
    corrected_value: str | None = None
    reviewed_by: str = "human_reviewer"

class ReviewResponse(BaseModel):
    review_id: int
    target_table: str
    target_id: int
    status: str
    updated_at: datetime

# --- Evaluation ---
class EvaluationRunSchema(BaseModel):
    run_id: int
    task: str
    run_timestamp: datetime
    dataset_version: str
    metrics: dict[str, Any]
    confusion_matrix: dict[str, Any] | None = None

    class Config:
        from_attributes = True
