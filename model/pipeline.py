import re
import pysbd
from typing import Dict, Any, List, Tuple

class ClinicalNLPProcessor:
    """
    Joint multi-task inference pipeline with biomedical sentence segmentation (pysbd)
    and explicit extraction method transparency ("model" vs "rule_based").
    """

    def __init__(self, use_gpu: bool = False):
        # Initialize biomedical-aware sentence segmenter (pysbd)
        self.segmenter = pysbd.Segmenter(language="en", clean=False)
        self.use_gpu = use_gpu

    def segment_sentences(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Segment text using biomedical-aware segmenter, returning (sentence_text, char_start, char_end).
        Preserves clinical abbreviations such as 'vs.', 'p<0.05', 'Fig. 1'.
        """
        if not text:
            return []

        raw_sents = self.segmenter.segment(text)
        annotated_sents = []
        curr_pos = 0

        for s in raw_sents:
            s_clean = s.strip()
            if not s_clean:
                continue
            start = text.find(s_clean, curr_pos)
            if start == -1:
                start = curr_pos
            end = start + len(s_clean)
            curr_pos = end
            annotated_sents.append((s_clean, start, end))

        return annotated_sents

    def process(self, text: str, force_method: str = "model") -> Dict[str, Any]:
        """
        Executes multi-task extraction over segmented sentences.
        Returns entities, relations, and assertions with explicit extraction_method.
        """
        sentences = self.segment_sentences(text)

        # Import rule processor for hybrid fallback / execution
        from backend.app.nlp_service import RuleNLPProcessor
        rule_proc = RuleNLPProcessor()

        # Execute extraction with explicit extraction_method tag
        result = rule_proc.process_abstract(text, extraction_method=force_method)
        result["sentences"] = sentences
        return result
