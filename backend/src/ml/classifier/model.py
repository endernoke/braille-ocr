from dataclasses import dataclass
from typing import Sequence

import torch
from torch import nn
import torch.nn.functional as F

@dataclass(frozen=True)
class ModelConfig:
    vocab_size: int
    num_classes: int
    embedding_dim: int = 16
    padding_idx: int = 0
    conv_channels: int = 128
    kernel_sizes: Sequence[int] = (3, 5, 7)
    dropout: float = 0.2

class BrailleClassifier(nn.Module):
    def __init__(self, config: ModelConfig) -> None:
        super().__init__()
        self.config = config
        self.embedding = nn.Embedding(
            num_embeddings=config.vocab_size,
            embedding_dim=config.embedding_dim,
            padding_idx=config.padding_idx,
        )
        self.convs = nn.ModuleList(
            [
                nn.Conv1d(
                    in_channels=config.embedding_dim,
                    out_channels=config.conv_channels,
                    kernel_size=k,
                    padding=k // 2,
                )
                for k in config.kernel_sizes
            ]
        )
        self.dropout = nn.Dropout(config.dropout)
        self.dense = nn.Linear(
            config.conv_channels * len(config.kernel_sizes),
            config.num_classes,
        )

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        # input_ids: (batch, seq_len)
        embedded = self.embedding(input_ids)  # (batch, seq_len, emb)
        features = embedded.permute(0, 2, 1)  # (batch, emb, seq_len)
        conv_outputs = []
        for conv in self.convs:
            activated = F.relu(conv(features))
            pooled = F.adaptive_max_pool1d(activated, 1).squeeze(2)  # (batch, conv_channels)
            conv_outputs.append(pooled)
        concat = torch.cat(conv_outputs, dim=1) # (batch, conv_channels * num_kernels)
        dropped = self.dropout(concat)
        return self.dense(dropped)

    @torch.no_grad()
    def predict(self, input_ids: torch.Tensor) -> torch.Tensor:
        logits = self.forward(input_ids)
        return torch.softmax(logits, dim=-1)


class TextPreprocessor:
    def __init__(self, alphabet: str, max_length: int = 20) -> None:
        self.char_to_idx = {char: idx+1 for idx, char in enumerate(alphabet)}
        self.pad_idx = 0
        self.max_length = max_length
    def preprocess(self, text: str, slice=False) -> list[int]:
        if len(text) > self.max_length:
            if slice:
                # Take a random slice
                start = torch.randint(0, len(text) - self.max_length + 1, (1,)).item()
                text = text[start:start+self.max_length]
            else:
                text = text[:self.max_length]
        indices = [self.char_to_idx.get(char, self.pad_idx) for char in text]
        if len(indices) < self.max_length:
            indices += [self.pad_idx] * (self.max_length - len(indices))
        return indices

