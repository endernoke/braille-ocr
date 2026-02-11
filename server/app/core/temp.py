from __future__ import annotations
import ultralytics
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
            

class RandomFlip:
    """Apply a random horizontal or vertical flip to an image with a given probability.

    This class performs random image flipping and updates corresponding instance annotations such as bounding boxes and
    keypoints.

    Attributes:
        p (float): Probability of applying the flip. Must be between 0 and 1.
        direction (str): Direction of flip, either 'horizontal' or 'vertical'.
        flip_idx (array-like): Index mapping for flipping keypoints, if applicable.

    Methods:
        __call__: Apply the random flip transformation to an image and its annotations.

    Examples:
        >>> transform = RandomFlip(p=0.5, direction="horizontal")
        >>> result = transform({"img": image, "instances": instances})
        >>> flipped_image = result["img"]
        >>> flipped_instances = result["instances"]
    """

    def __init__(self, p: float = 0.5, direction: str = "horizontal", flip_idx: list[int] | None = None) -> None:
        """Initialize the RandomFlip class with probability and direction.

        This class applies a random horizontal or vertical flip to an image with a given probability. It also updates
        any instances (bounding boxes, keypoints, etc.) accordingly.

        Args:
            p (float): The probability of applying the flip. Must be between 0 and 1.
            direction (str): The direction to apply the flip. Must be 'horizontal' or 'vertical'.
            flip_idx (list[int] | None): Index mapping for flipping keypoints, if any.

        Raises:
            AssertionError: If direction is not 'horizontal' or 'vertical', or if p is not between 0 and 1.
        """
        assert direction in {"horizontal", "vertical"}, f"Support direction `horizontal` or `vertical`, got {direction}"
        assert 0 <= p <= 1.0, f"The probability should be in range [0, 1], but got {p}."

        self.p = p
        self.direction = direction
        self.flip_idx = flip_idx

    def __call__(self, labels: dict[str, any]) -> dict[str, any]:
        """Apply random flip to an image and update any instances like bounding boxes or keypoints accordingly.

        This method randomly flips the input image either horizontally or vertically based on the initialized
        probability and direction. It also updates the corresponding instances (bounding boxes, keypoints) to match the
        flipped image.

        Args:
            labels (dict[str, any]): A dictionary containing the following keys:
                - 'img' (np.ndarray): The image to be flipped.
                - 'instances' (ultralytics.utils.instance.Instances): Object containing boxes and optionally keypoints.

        Returns:
            (dict[str, any]): The same dictionary with the flipped image and updated instances:
                - 'img' (np.ndarray): The flipped image.
                - 'instances' (ultralytics.utils.instance.Instances): Updated instances matching the flipped image.

        Examples:
            >>> labels = {"img": np.random.rand(640, 640, 3), "instances": Instances(...)}
            >>> random_flip = RandomFlip(p=0.5, direction="horizontal")
            >>> flipped_labels = random_flip(labels)
        """
        img = labels["img"]
        instances = labels.pop("instances")
        instances.convert_bbox(format="xywh")
        h, w = img.shape[:2]
        h = 1 if instances.normalized else h
        w = 1 if instances.normalized else w

        # WARNING: two separate if and calls to random.random() intentional for reproducibility with older versions
        if self.direction == "vertical" and random.random() < self.p:
            img = np.flipud(img)
            instances.flipud(h)
            if self.flip_idx is not None and instances.keypoints is not None:
                instances.keypoints = np.ascontiguousarray(instances.keypoints[:, self.flip_idx, :])
        if self.direction == "horizontal" and random.random() < self.p:
            img = np.fliplr(img)
            instances.fliplr(w)
            if self.flip_idx is not None and instances.keypoints is not None:
                instances.keypoints = np.ascontiguousarray(instances.keypoints[:, self.flip_idx, :])
        labels["img"] = np.ascontiguousarray(img)
        labels["instances"] = instances
        return labels



custom_augmentations = [
    A.Rotate(limit=5, p=0.5),
    # A.(0.1, p=0.5),
    # A.RandomCrop(height=416, width=416, p=1),
]



# model = YOLO("yolo11n.pt")
# model.train(
#     data="data/coco128.yaml",
#     epochs=3,
#     trainer=ZScoreTrainer,
#     name="yolo11n_coco128",
#     exist_ok=True,
#     augmentations=custom_augmentations
#     )