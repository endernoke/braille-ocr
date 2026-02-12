import torch
import torch.nn as nn


class TextClassifier(nn.Module):    
    def __init__(self, num_classes: int = 10, vocab_size: int = 10000):
        """Initialize classifier.
        
        Args:
            num_classes: Number of classification categories
            vocab_size: Size of vocabulary
        """
        super().__init__()
        
        # Stub: simple embedding + LSTM
        self.embedding = nn.Embedding(vocab_size, 128)
        self.lstm = nn.LSTM(128, 256, batch_first=True, num_layers=2)
        self.classifier = nn.Linear(256, num_classes)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass.
        
        Args:
            x: Input token IDs [B, seq_len]
            
        Returns:
            logits: Class logits [B, num_classes]
        """
        embedded = self.embedding(x)  # [B, seq_len, 128]
        lstm_out, (hidden, _) = self.lstm(embedded)
        # Use last hidden state
        logits = self.classifier(hidden[-1])  # [B, num_classes]
        return logits
