
import torch
import torch.nn.functional as F
from torch import nn


class NERHead(nn.Module):
    """
    Token classification head for BIO Named Entity Recognition.
    """
    BIO_LABELS = [
        "O",
        "B-Disease", "I-Disease",
        "B-Drug", "I-Drug",
        "B-Sample Size", "I-Sample Size",
        "B-Endpoint", "I-Endpoint"
    ]

    def __init__(self, hidden_size: int = 768, num_labels: int = len(BIO_LABELS)):
        super().__init__()
        self.dropout = nn.Dropout(0.1)
        self.classifier = nn.Linear(hidden_size, num_labels)

    def forward(self, sequence_output: torch.Tensor):
        # sequence_output: (batch_size, seq_len, hidden_size)
        x = self.dropout(sequence_output)
        logits = self.classifier(x) # (batch_size, seq_len, num_labels)
        probs = F.softmax(logits, dim=-1)
        return logits, probs

class RelationExtractionHead(nn.Module):
    """
    Pairwise entity relation classifier head.
    Concatenates hidden states of subject entity and object entity embeddings.
    """
    RELATION_LABELS = [
        "NO_RELATION",
        "Drug→Disease",
        "Drug→Cohort",
        "Outcome-link"
    ]

    def __init__(self, hidden_size: int = 768, num_classes: int = len(RELATION_LABELS)):
        super().__init__()
        # Input dimension is 2 * hidden_size for pair concatenation
        self.dropout = nn.Dropout(0.1)
        self.dense = nn.Linear(hidden_size * 2, hidden_size)
        self.classifier = nn.Linear(hidden_size, num_classes)

    def forward(self, subject_embed: torch.Tensor, object_embed: torch.Tensor):
        # subject_embed: (batch_size, hidden_size)
        # object_embed: (batch_size, hidden_size)
        pair_embed = torch.cat([subject_embed, object_embed], dim=-1) # (batch_size, 2*hidden_size)
        x = self.dropout(pair_embed)
        x = torch.tanh(self.dense(x))
        logits = self.classifier(x)
        probs = F.softmax(logits, dim=-1)
        return logits, probs

class AssertionDetectionHead(nn.Module):
    """
    Assertion status classifier head (Positive, Negated, Conditional).
    """
    ASSERTION_LABELS = [
        "Positive",
        "Negated",
        "Conditional"
    ]

    def __init__(self, hidden_size: int = 768, num_classes: int = len(ASSERTION_LABELS)):
        super().__init__()
        self.dropout = nn.Dropout(0.1)
        self.classifier = nn.Linear(hidden_size, num_classes)

    def forward(self, relation_context_embed: torch.Tensor):
        # relation_context_embed: (batch_size, hidden_size)
        x = self.dropout(relation_context_embed)
        logits = self.classifier(x)
        probs = F.softmax(logits, dim=-1)
        return logits, probs
