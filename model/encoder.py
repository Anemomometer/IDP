import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer

class SharedBiomedicalEncoder(nn.Module):
    """
    Shared biomedical transformer backbone (PubMedBERT) producing contextual token embeddings.
    Shared across NER, Relation Extraction, and Assertion Detection task heads.
    """
    DEFAULT_MODEL_NAME = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext"

    def __init__(self, model_name_or_path: str = None):
        super().__init__()
        self.model_name = model_name_or_path or self.DEFAULT_MODEL_NAME
        try:
            self.encoder = AutoModel.from_pretrained(self.model_name)
        except Exception:
            # Fallback to standard bert-base-uncased if network downloads fail or offline
            self.model_name = "bert-base-uncased"
            self.encoder = AutoModel.from_pretrained(self.model_name)

        self.hidden_size = self.encoder.config.hidden_size

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor = None, token_type_ids: torch.Tensor = None):
        outputs = self.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            return_dict=True
        )
        # last_hidden_state: (batch_size, seq_len, hidden_size)
        # pooler_output: (batch_size, hidden_size)
        return outputs.last_hidden_state, outputs.pooler_output
