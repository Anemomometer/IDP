
import torch
from torch import nn

from .encoder import SharedBiomedicalEncoder
from .heads import AssertionDetectionHead, NERHead, RelationExtractionHead


class MultiTaskClinicalModel(nn.Module):
    """
    Joint multi-task PyTorch model architecture combining a shared biomedical encoder
    with three task-specific classification heads (NER, RE, AD).
    """

    def __init__(self, model_name_or_path: str = None):
        super().__init__()
        self.encoder = SharedBiomedicalEncoder(model_name_or_path)
        hidden_size = self.encoder.hidden_size

        self.ner_head = NERHead(hidden_size=hidden_size)
        self.re_head = RelationExtractionHead(hidden_size=hidden_size)
        self.ad_head = AssertionDetectionHead(hidden_size=hidden_size)

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor = None,
        token_type_ids: torch.Tensor = None,
        subj_indices: torch.Tensor | None = None,
        obj_indices: torch.Tensor | None = None
    ):
        last_hidden, pooler_output = self.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids
        )

        # 1. NER Forward Pass
        ner_logits, ner_probs = self.ner_head(last_hidden)

        # 2. Relation Extraction Forward Pass (if entity indices provided)
        re_logits, re_probs = None, None
        if subj_indices is not None and obj_indices is not None:
            # Extract mean embeddings for subject and object spans
            subj_embeds = torch.stack([last_hidden[i, idx, :].mean(dim=0) for i, idx in enumerate(subj_indices)])
            obj_embeds = torch.stack([last_hidden[i, idx, :].mean(dim=0) for i, idx in enumerate(obj_indices)])
            re_logits, re_probs = self.re_head(subj_embeds, obj_embeds)

        # 3. Assertion Detection Forward Pass (uses pooler/context embedding)
        ad_logits, ad_probs = self.ad_head(pooler_output)

        return {
            "ner_logits": ner_logits,
            "ner_probs": ner_probs,
            "re_logits": re_logits,
            "re_probs": re_probs,
            "ad_logits": ad_logits,
            "ad_probs": ad_probs
        }

class MultiTaskLoss(nn.Module):
    """
    Computes joint multi-task loss with tunable per-task weights (lambda_ner, lambda_re, lambda_ad).
    """

    def __init__(self, lambda_ner: float = 1.0, lambda_re: float = 1.0, lambda_ad: float = 1.0):
        super().__init__()
        self.lambda_ner = lambda_ner
        self.lambda_re = lambda_re
        self.lambda_ad = lambda_ad

        self.ner_criterion = nn.CrossEntropyLoss(ignore_index=-100)
        self.re_criterion = nn.CrossEntropyLoss()
        self.ad_criterion = nn.CrossEntropyLoss()

    def forward(
        self,
        predictions: dict[str, torch.Tensor],
        ner_targets: torch.Tensor = None,
        re_targets: torch.Tensor = None,
        ad_targets: torch.Tensor = None
    ) -> dict[str, torch.Tensor]:

        total_loss = 0.0
        loss_components = {}

        if ner_targets is not None and predictions["ner_logits"] is not None:
            ner_loss = self.ner_criterion(
                predictions["ner_logits"].view(-1, len(NERHead.BIO_LABELS)),
                ner_targets.view(-1)
            )
            total_loss += self.lambda_ner * ner_loss
            loss_components["ner_loss"] = ner_loss.item()

        if re_targets is not None and predictions["re_logits"] is not None:
            re_loss = self.re_criterion(predictions["re_logits"], re_targets)
            total_loss += self.lambda_re * re_loss
            loss_components["re_loss"] = re_loss.item()

        if ad_targets is not None and predictions["ad_logits"] is not None:
            ad_loss = self.ad_criterion(predictions["ad_logits"], ad_targets)
            total_loss += self.lambda_ad * ad_loss
            loss_components["ad_loss"] = ad_loss.item()

        loss_components["total_loss"] = total_loss if isinstance(total_loss, float) else total_loss.item()
        return total_loss, loss_components
