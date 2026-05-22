from __future__ import annotations

import json
from functools import lru_cache

import torch
from langchain_core.tools import tool
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForObjectDetection

MODEL_ID = "mserrasa/detr-resnet-50_finetuned_VinBigData"
SCORE_THRESHOLD = 0.3


@lru_cache(maxsize=1)
def _load():
	processor = AutoImageProcessor.from_pretrained(MODEL_ID)
	model = AutoModelForObjectDetection.from_pretrained(MODEL_ID)
	model.eval()
	if torch.cuda.is_available():
		model = model.cuda()
	return processor, model


@tool("vinbigdata_cv")
def vinbigdata_cv(image_path: str) -> str:
	"""Run DETR object detection fine-tuned on VinBigData and return findings as a JSON string.

	Detects the VinBigData chest X-ray abnormality classes with bounding boxes.
	Output JSON shape:
	{"findings": [{"label": str, "score": float, "box": [x1, y1, x2, y2]}, ...]}
	sorted by score desc.
	"""
	processor, model = _load()
	image = Image.open(image_path).convert("RGB")
	inputs = processor(images=image, return_tensors="pt")

	if torch.cuda.is_available():
		inputs = {k: v.cuda() for k, v in inputs.items()}

	with torch.no_grad():
		outputs = model(**inputs)

	target_sizes = torch.tensor([image.size[::-1]])
	if torch.cuda.is_available():
		target_sizes = target_sizes.cuda()

	results = processor.post_process_object_detection(
		outputs, target_sizes=target_sizes, threshold=SCORE_THRESHOLD
	)[0]

	findings = []
	for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
		findings.append(
			{
				"label": model.config.id2label[label.item()],
				"score": round(score.item(), 3),
				"box": [round(c, 1) for c in box.cpu().tolist()],
			}
		)
	findings.sort(key=lambda x: x["score"], reverse=True)

	return json.dumps({"findings": findings}, ensure_ascii=False)
