import json
import os
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from .models_db import EvaluationRun
from .nlp_service import RuleNLPProcessor


class EvaluationHarness:
    """
    Evaluation harness for scoring NER, RE, and AD tasks against gold_standard.json benchmark set.
    Generates confusion matrices and per-class + macro-averaged P/R/F1 scores.
    """

    # Normalization map: gold standard relation labels → evaluation class names
    RE_LABEL_MAP = {
        "DRUG→DISEASE": "TREATS",
        "DRUG->DISEASE": "TREATS",
        "DRUG_DISEASE": "TREATS",
        "DRUG→COHORT": "TESTED_IN",
        "DRUG->COHORT": "TESTED_IN",
        "DRUG_COHORT": "TESTED_IN",
        "OUTCOME-LINK": "MEASURED_BY",
        "OUTCOME_LINK": "MEASURED_BY",
        # Pass-through for already-normalized labels
        "TREATS": "TREATS",
        "TESTED_IN": "TESTED_IN",
        "MEASURED_BY": "MEASURED_BY",
    }

    # Normalization map: gold standard assertion labels → evaluation class names
    AD_LABEL_MAP = {
        "POSITIVE": "PRESENT_POSITIVE",
        "NEGATED": "ABSENT_NEGATED",
        "NEGATIVE": "ABSENT_NEGATED",
        # Pass-through for already-normalized labels
        "PRESENT_POSITIVE": "PRESENT_POSITIVE",
        "ABSENT_NEGATED": "ABSENT_NEGATED",
        "CONDITIONAL": "CONDITIONAL",
    }

    def __init__(self, gold_standard_path: str = None):
        if not gold_standard_path:
            gold_standard_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data", "gold_standard.json"
            )
        self.gold_standard_path = gold_standard_path
        self.processor = RuleNLPProcessor()

    def _normalize_re_label(self, label: str) -> str | None:
        """Normalize a relation type label from gold or predicted data to a standard class name."""
        normalized = label.upper().replace(" ", "_").replace("\u2192", "->")
        return self.RE_LABEL_MAP.get(normalized)

    def _normalize_ad_label(self, label: str) -> str | None:
        """Normalize an assertion type label from gold or predicted data to a standard class name."""
        normalized = label.upper().replace(" ", "_")
        return self.AD_LABEL_MAP.get(normalized)

    def load_gold_data(self) -> list[dict[str, Any]]:
        if not os.path.exists(self.gold_standard_path):
            return []
        with open(self.gold_standard_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def calculate_prf1(self, tp: int, fp: int, fn: int) -> dict[str, float]:
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        return {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "tp": tp,
            "fp": fp,
            "fn": fn
        }

    def run_evaluation(self, db: Session = None, task: str = "ALL", dataset_version: str = "v1.0-gold") -> dict[str, Any]:
        gold_items = self.load_gold_data()

        # Target classes per task
        ner_classes = ["DISEASE", "DRUG", "SAMPLE_SIZE", "ENDPOINT"]
        re_classes = ["TREATS", "TESTED_IN", "MEASURED_BY"]
        ad_classes = ["PRESENT_POSITIVE", "ABSENT_NEGATED", "CONDITIONAL"]

        # Trackers
        ner_stats = {c: {"tp": 0, "fp": 0, "fn": 0} for c in ner_classes}
        re_stats = {c: {"tp": 0, "fp": 0, "fn": 0} for c in re_classes}
        ad_stats = {c: {"tp": 0, "fp": 0, "fn": 0} for c in ad_classes}

        # Confusion matrix for AD: rows=true, cols=pred
        ad_cm = {true_c: {pred_c: 0 for pred_c in ad_classes} for true_c in ad_classes}

        for item in gold_items:
            text = item.get("normalized_text") or item.get("raw_text") or ""
            pred = self.processor.process_abstract(text, extraction_method="model")

            gold_entities = item.get("gold_entities", [])
            pred_entities = pred.get("entities", [])

            # --- NER Evaluation ---
            for c in ner_classes:
                g_spans = set((e["char_start"], e["char_end"]) for e in gold_entities if e.get("entity_type", "").upper().replace(" ", "_") == c)
                p_spans = set((e["char_start"], e["char_end"]) for e in pred_entities if e.get("entity_type", "").upper().replace(" ", "_") == c)

                tp = len(g_spans.intersection(p_spans))
                fp = len(p_spans - g_spans)
                fn = len(g_spans - p_spans)

                ner_stats[c]["tp"] += tp
                ner_stats[c]["fp"] += fp
                ner_stats[c]["fn"] += fn

            # --- RE & AD Evaluation ---
            gold_relations = item.get("gold_relations", [])
            pred_relations = pred.get("relations", [])
            pred_assertions = pred.get("assertions", [])

            gold_ent_map = {e["entity_id"]: e["text_span"] for e in gold_entities}
            pred_ent_map = {e["entity_id"]: e["text_span"] for e in pred_entities}

            for c in re_classes:
                g_rels = set(
                    (r.get("subject_text") or gold_ent_map.get(r.get("subject_entity_id")),
                     r.get("object_text") or gold_ent_map.get(r.get("object_entity_id")))
                    for r in gold_relations if self._normalize_re_label(r.get("relation_type", "")) == c
                )
                p_rels = set(
                    (r.get("subject_text") or pred_ent_map.get(r.get("subject_entity_id")),
                     r.get("object_text") or pred_ent_map.get(r.get("object_entity_id")))
                    for r in pred_relations if self._normalize_re_label(r.get("relation_type", "")) == c
                )

                tp = len(g_rels.intersection(p_rels))
                fp = len(p_rels - g_rels)
                fn = len(g_rels - p_rels)

                re_stats[c]["tp"] += tp
                re_stats[c]["fp"] += fp
                re_stats[c]["fn"] += fn

            # AD Evaluation & CM
            gold_assertions = item.get("gold_assertions", [])
            
            gold_rel_map = {}
            for r in gold_relations:
                sub_txt = r.get("subject_text") or gold_ent_map.get(r.get("subject_entity_id"))
                obj_txt = r.get("object_text") or gold_ent_map.get(r.get("object_entity_id"))
                rtype = self._normalize_re_label(r.get("relation_type", ""))
                gold_rel_map[r.get("relation_id")] = (sub_txt, obj_txt, rtype)
                
            pred_rel_assert_map = {}
            for pa in pred_assertions:
                rel_id = pa.get("relation_id")
                rel = next((pr for pr in pred_relations if pr.get("relation_id") == rel_id), None)
                if rel:
                    sub_txt = rel.get("subject_text") or pred_ent_map.get(rel.get("subject_entity_id"))
                    obj_txt = rel.get("object_text") or pred_ent_map.get(rel.get("object_entity_id"))
                    rtype = self._normalize_re_label(rel.get("relation_type", ""))
                    pred_rel_assert_map[(sub_txt, obj_txt, rtype)] = self._normalize_ad_label(pa.get("assertion_type", "PRESENT_POSITIVE")) or "PRESENT_POSITIVE"

            for ga in gold_assertions:
                true_label = self._normalize_ad_label(ga.get("assertion_type", "PRESENT_POSITIVE"))
                if not true_label: continue
                
                if true_label in ad_classes:
                    rel_tuple = gold_rel_map.get(ga.get("relation_id"))
                    
                    pred_label = "PRESENT_POSITIVE" # Default if relation wasn't extracted
                    if rel_tuple and rel_tuple in pred_rel_assert_map:
                        pred_label = pred_rel_assert_map[rel_tuple]
                        
                    if pred_label in ad_classes:
                        ad_cm[true_label][pred_label] += 1
                        if true_label == pred_label:
                            ad_stats[true_label]["tp"] += 1
                        else:
                            ad_stats[pred_label]["fp"] += 1
                            ad_stats[true_label]["fn"] += 1

        # Format NER metrics
        ner_per_class = {c: self.calculate_prf1(**ner_stats[c]) for c in ner_classes}
        ner_macro_p = sum(ner_per_class[c]["precision"] for c in ner_classes) / len(ner_classes)
        ner_macro_r = sum(ner_per_class[c]["recall"] for c in ner_classes) / len(ner_classes)
        ner_macro_f1 = sum(ner_per_class[c]["f1"] for c in ner_classes) / len(ner_classes)

        # Format RE metrics
        re_per_class = {c: self.calculate_prf1(**re_stats[c]) for c in re_classes}
        re_macro_p = sum(re_per_class[c]["precision"] for c in re_classes) / len(re_classes)
        re_macro_r = sum(re_per_class[c]["recall"] for c in re_classes) / len(re_classes)
        re_macro_f1 = sum(re_per_class[c]["f1"] for c in re_classes) / len(re_classes)

        # Format AD metrics
        ad_per_class = {c: self.calculate_prf1(**ad_stats[c]) for c in ad_classes}
        ad_macro_p = sum(ad_per_class[c]["precision"] for c in ad_classes) / len(ad_classes)
        ad_macro_r = sum(ad_per_class[c]["recall"] for c in ad_classes) / len(ad_classes)
        ad_macro_f1 = sum(ad_per_class[c]["f1"] for c in ad_classes) / len(ad_classes)

        metrics = {
            "NER": {
                "per_class": ner_per_class,
                "macro": {"precision": round(ner_macro_p, 4), "recall": round(ner_macro_r, 4), "f1": round(ner_macro_f1, 4)}
            },
            "RE": {
                "per_class": re_per_class,
                "macro": {"precision": round(re_macro_p, 4), "recall": round(re_macro_r, 4), "f1": round(re_macro_f1, 4)}
            },
            "AD": {
                "per_class": ad_per_class,
                "macro": {"precision": round(ad_macro_p, 4), "recall": round(ad_macro_r, 4), "f1": round(ad_macro_f1, 4)}
            }
        }

        eval_run_rec = None
        if db:
            eval_run_rec = EvaluationRun(
                task=task,
                run_timestamp=datetime.utcnow(),
                dataset_version=dataset_version,
                metrics_json=json.dumps(metrics),
                confusion_matrix_json=json.dumps(ad_cm)
            )
            db.add(eval_run_rec)
            db.commit()
            db.refresh(eval_run_rec)

        return {
            "run_id": eval_run_rec.run_id if eval_run_rec else 1,
            "task": task,
            "run_timestamp": eval_run_rec.run_timestamp.isoformat() if eval_run_rec else datetime.utcnow().isoformat(),
            "dataset_version": dataset_version,
            "metrics": metrics,
            "confusion_matrix": ad_cm
        }
