from __future__ import annotations

import json
import os
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
import torch
from langchain_core.tools import tool
from PIL import Image

_YOLO5_DIR = Path(__file__).parent / "yolo5"
if str(_YOLO5_DIR) not in sys.path:
	sys.path.insert(0, str(_YOLO5_DIR))

from utils.datasets import letterbox  # noqa: E402
from utils.general import non_max_suppression, scale_coords  # noqa: E402

WEIGHTS_PATH = Path(__file__).parent / "weights" / "stage1_fold0.pt"
IMG_SIZE = 640
CONF_THRES = 0.05
IOU_THRES = 0.4

# VinBigData 14 abnormality classes 
CLASS_NAMES = [
	"Aortic enlargement",
	"Atelectasis",
	"Calcification",
	"Cardiomegaly",
	"Consolidation",
	"ILD",
	"Infiltration",
	"Lung Opacity",
	"Nodule/Mass",
	"Other lesion",
	"Pleural effusion",
	"Pleural thickening",
	"Pneumothorax",
	"Pulmonary fibrosis",
]


def _load_image(path: str) -> np.ndarray:
	"""Load PNG/JPG via PIL or DICOM via pydicom -> uint8 RGB ndarray (H, W, 3)."""
	if path.lower().endswith((".dcm", ".dicom")):
		import pydicom

		ds = pydicom.dcmread(path)
		arr = ds.pixel_array.astype(np.float32)
		if getattr(ds, "PhotometricInterpretation", "") == "MONOCHROME1":
			arr = arr.max() - arr
		arr = arr - arr.min()
		if arr.max() > 0:
			arr = arr / arr.max() * 255.0
		arr = arr.astype(np.uint8)
		return np.stack([arr, arr, arr], axis=-1)
	img = Image.open(path).convert("RGB")
	return np.array(img)


@lru_cache(maxsize=1)
def _load_model():
	device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
	ckpt = torch.load(str(WEIGHTS_PATH), map_location=device, weights_only=False)
	model = ckpt["model"].float().to(device).eval()
	return model, device


@tool("vinbigdata_cv")
def vinbigdata_cv(image_path: str) -> str:
	"""Run YOLOv5x VinBigData (Kaggle 2nd-place fold) detection on a chest X-ray.

	Accepts PNG/JPG or DICOM. Output JSON:
	{"findings": [{"label": str, "score": float, "box": [x1, y1, x2, y2]}, ...]}
	box coords are in original image pixel space, sorted by score desc.
	If empty -> No finding.
	"""
	model, device = _load_model()
	img0 = _load_image(image_path)  # HWC uint8 RGB
	img = letterbox(img0, new_shape=IMG_SIZE)[0]
	img = img.transpose(2, 0, 1)  # HWC -> CHW
	img = np.ascontiguousarray(img)
	tensor = torch.from_numpy(img).to(device).float() / 255.0
	tensor = tensor.unsqueeze(0)

	with torch.no_grad():
		pred = model(tensor, augment=False)[0]
	pred = non_max_suppression(pred, CONF_THRES, IOU_THRES)

	findings = []
	for det in pred:
		if det is None or not len(det):
			continue
		det[:, :4] = scale_coords(tensor.shape[2:], det[:, :4], img0.shape).round()
		for *xyxy, conf, cls in det:
			findings.append(
				{
					"label": CLASS_NAMES[int(cls)],
					"score": round(float(conf), 4),
					"box": [round(float(c), 1) for c in xyxy],
				}
			)
	findings.sort(key=lambda x: x["score"], reverse=True)

	return json.dumps({"findings": findings}, ensure_ascii=False)
