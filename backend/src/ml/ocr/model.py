from __future__ import annotations
from typing import Any
import albumentations as A
import random
from copy import copy
from ultralytics import YOLO
from ultralytics.models.yolo.detect.train import DetectionTrainer
from ultralytics.models.yolo.detect.val import DetectionValidator
from ultralytics.models.yolo.detect.predict import DetectionPredictor
from ultralytics.utils import nms, ops
import numpy as np

import torch
from ultralytics.models.yolo.detect.train import DetectionTrainer

def normalize_image_batch(imgs: torch.Tensor) -> torch.Tensor:
    """
    Normalize batch of images using the formula:
    $$x_c = \frac{I_c - m}{(3 \cdot \max(s, 0.1 * 255)}$$
    where:
    - $I_c$ is the pixel value in channel c
    - $m$ is the mean pixel value across all channels
    - $s$ is the standard deviation of pixel values across all channels
    """
    mean = imgs.mean(dim=(2, 3), keepdim=True)
    std = imgs.std(dim=(2, 3), keepdim=True)
    denominator = 3 * std.clamp_min(min=0.1 * 255)  # for stability
    return (imgs - mean) / denominator

def denormalize_image_batch(batch: torch.Tensor) -> torch.Tensor:
    """
    Approximately denormalize batch of images to [0, 255]
    """
    # ~99.7% of values should be in [-1, 1] after normalization
    return (batch.clamp(-1, 1) + 0.5) * 255

class ZScorePredictor(DetectionPredictor):
    def preprocess(self, im):
        im = super().preprocess(im)
        # self.args.visualize=True
        # self.args.max_det = 10000
        return normalize_image_batch(im) 

    
    def postprocess(self, preds, img, orig_imgs, **kwargs):
        """Post-process predictions and return a list of Results objects.

        This method applies non-maximum suppression to raw model predictions and prepares them for visualization and
        further analysis.

        Args:
            preds (torch.Tensor): Raw predictions from the model.
            img (torch.Tensor): Processed input image tensor in model input format.
            orig_imgs (torch.Tensor | list): Original input images before preprocessing.
            **kwargs (any): Additional keyword arguments.

        Returns:
            (list): List of Results objects containing the post-processed predictions.

        Examples:
            >>> predictor = DetectionPredictor(overrides=dict(model="yolo11n.pt"))
            >>> results = predictor.predict("path/to/image.jpg")
            >>> processed_results = predictor.postprocess(preds, img, orig_imgs)
        """
        save_feats = getattr(self, "_feats", None) is not None
        preds = nms.non_max_suppression(
            preds,
            self.args.conf,
            self.args.iou,
            self.args.classes,
            self.args.agnostic_nms,
            max_det=self.args.max_det,
            nc=0 if self.args.task == "detect" else len(self.model.names),
            end2end=getattr(self.model, "end2end", False),
            rotated=self.args.task == "obb",
            return_idxs=save_feats,
        )

        if not isinstance(orig_imgs, list):  # input images are a torch.Tensor, not a list
            orig_imgs = denormalize_image_batch(orig_imgs).permute(0, 2, 3, 1).contiguous().clamp(0, 255).byte().cpu().numpy()[..., ::-1]

        if save_feats:
            obj_feats = self.get_obj_feats(self._feats, preds[1])
            preds = preds[0]

        results = self.construct_results(preds, img, orig_imgs, **kwargs)

        if save_feats:
            for r, f in zip(results, obj_feats):
                r.feats = f  # add object features to results

        return results


class ZScoreValidator(DetectionValidator):
    def preprocess(self, batch: dict) -> dict:
        self.args.max_det = 99999
        batch = super().preprocess(batch)  # moves to device + scales
        batch["img"] = normalize_image_batch(batch["img"])
        return batch

class ZScoreTrainer(DetectionTrainer):
    def preprocess(self, batch: dict) -> dict:
        batch = super().preprocess_batch(batch)  # moves to device + scales
        batch["img"] = normalize_image_batch(batch["img"])
        return batch
    def get_validator(self):
        super().get_validator()  # discard returned validator
        return ZScoreValidator(
            self.test_loader, save_dir=self.save_dir, args=copy(self.args), _callbacks=self.callbacks
        )

class CustomYOLO(YOLO):
    @property
    def task_map(self) -> dict[str, dict[str, Any]]:
        """Map head to model, trainer, validator, and predictor classes."""
        task_map = super().task_map
        task_map["detect"].update({
            "trainer": ZScoreTrainer,
            "validator": ZScoreValidator,
            "predictor": ZScorePredictor,
        })
        return task_map


custom_augmentations = [
    A.Rotate(limit=5, p=0.5),
]
