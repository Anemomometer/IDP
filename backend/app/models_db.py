from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from .database import Base

class Abstract(Base):
    __tablename__ = "abstracts"

    abstract_id = Column(String, primary_key=True, index=True) # PMID
    title = Column(Text, nullable=False)
    raw_text = Column(Text, nullable=False)
    normalized_text = Column(Text, nullable=False)
    source_query = Column(String, nullable=True)
    retrieved_at = Column(DateTime, default=datetime.utcnow)

    entities = relationship("Entity", back_populates="abstract", cascade="all, delete-orphan")
    relations = relationship("Relation", back_populates="abstract", cascade="all, delete-orphan")

class Entity(Base):
    __tablename__ = "entities"

    entity_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    abstract_id = Column(String, ForeignKey("abstracts.abstract_id", ondelete="CASCADE"), nullable=False, index=True)
    entity_type = Column(String, nullable=False) # Disease, Drug, Sample Size, Endpoint
    text_span = Column(Text, nullable=False)
    char_start = Column(Integer, nullable=False)
    char_end = Column(Integer, nullable=False)
    confidence_score = Column(Float, nullable=False, default=1.0)
    extraction_method = Column(String, nullable=False, default="model") # "model" | "rule_based"
    review_status = Column(String, nullable=False, default="unreviewed") # "unreviewed" | "approved" | "corrected" | "rejected"

    abstract = relationship("Abstract", back_populates="entities")
    subject_relations = relationship("Relation", foreign_keys="Relation.subject_entity_id", back_populates="subject_entity", cascade="all, delete-orphan")
    object_relations = relationship("Relation", foreign_keys="Relation.object_entity_id", back_populates="object_entity", cascade="all, delete-orphan")

class Relation(Base):
    __tablename__ = "relations"

    relation_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    abstract_id = Column(String, ForeignKey("abstracts.abstract_id", ondelete="CASCADE"), nullable=False, index=True)
    subject_entity_id = Column(Integer, ForeignKey("entities.entity_id", ondelete="CASCADE"), nullable=False, index=True)
    object_entity_id = Column(Integer, ForeignKey("entities.entity_id", ondelete="CASCADE"), nullable=False, index=True)
    relation_type = Column(String, nullable=False) # Drug→Disease, Drug→Cohort, Outcome-link
    confidence_score = Column(Float, nullable=False, default=1.0)
    extraction_method = Column(String, nullable=False, default="model") # "model" | "rule_based"
    review_status = Column(String, nullable=False, default="unreviewed") # "unreviewed" | "approved" | "corrected" | "rejected"

    abstract = relationship("Abstract", back_populates="relations")
    subject_entity = relationship("Entity", foreign_keys=[subject_entity_id], back_populates="subject_relations")
    object_entity = relationship("Entity", foreign_keys=[object_entity_id], back_populates="object_relations")
    assertions = relationship("Assertion", back_populates="relation", cascade="all, delete-orphan")

class Assertion(Base):
    __tablename__ = "assertions"

    assertion_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    relation_id = Column(Integer, ForeignKey("relations.relation_id", ondelete="CASCADE"), nullable=False, index=True)
    assertion_type = Column(String, nullable=False) # Positive, Negated, Conditional
    confidence_score = Column(Float, nullable=False, default=1.0)
    extraction_method = Column(String, nullable=False, default="model") # "model" | "rule_based"
    review_status = Column(String, nullable=False, default="unreviewed") # "unreviewed" | "approved" | "corrected" | "rejected"

    relation = relationship("Relation", back_populates="assertions")

class ReviewLog(Base):
    __tablename__ = "review_log"

    review_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    target_table = Column(String, nullable=False) # entities, relations, assertions
    target_id = Column(Integer, nullable=False)
    reviewer_status = Column(String, nullable=False) # approved, corrected, rejected
    corrected_value = Column(Text, nullable=True)
    reviewed_by = Column(String, nullable=False, default="human_reviewer")
    reviewed_at = Column(DateTime, default=datetime.utcnow)

Index("idx_review_log_target", ReviewLog.target_table, ReviewLog.target_id)

class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    run_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    task = Column(String, nullable=False) # NER, RE, AD, ALL
    run_timestamp = Column(DateTime, default=datetime.utcnow)
    dataset_version = Column(String, nullable=False, default="v1.0-gold")
    metrics_json = Column(Text, nullable=False) # P/R/F1 per class and macro
    confusion_matrix_json = Column(Text, nullable=True) # JSON matrix
