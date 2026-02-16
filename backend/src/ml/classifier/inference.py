from pathlib import Path
import json
import torch

from .model import BrailleClassifier, TextPreprocessor, ModelConfig
from ..device import get_device


class ClassifierInference:
    def __init__(self, model_path: str):
        checkpoint = torch.load(model_path, map_location="cpu")
        alphabet = checkpoint["alphabet"]
        self.preprocessor = TextPreprocessor(alphabet, max_length=20)
        self.label_names = checkpoint["label_names"]

        self.model_config = ModelConfig(**checkpoint["config"])
        self.model = BrailleClassifier(self.model_config)
        self.model.load_state_dict(checkpoint["model_state"])
        self.model.eval()

        with open(Path(__file__).parent.parent.parent / "braille" / "braille_chars.json", "r") as f:
            self.braille_unicode_mapping = json.load(f)

    def predict(self, text: str) -> tuple[str, float]:
        text = "".join([self.braille_unicode_mapping.get(char, "") for char in text])
        processed_text = self.preprocessor.preprocess(text)
        input_ids = torch.tensor([processed_text], dtype=torch.long)
        probs = self.model.predict(input_ids)
        return self.top_k_predictions(probs, self.label_names, k=1)[0][0]

    def top_k_predictions(
        self,
        probs: torch.Tensor,
        labels: list[str],
        k: int = 2,
    ) -> list[list[tuple[str, float]]]:
        values, indices = torch.topk(probs, k=k, dim=-1)
        results: list[list[tuple[str, float]]] = []
        for row_values, row_indices in zip(values, indices):
            row = []
            for score, idx in zip(row_values.tolist(), row_indices.tolist()):
                row.append((labels[idx], float(score)))
            results.append(row)
        return results
