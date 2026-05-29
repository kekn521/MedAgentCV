# Data — VinBigData chest X-ray dataset (Part 1)

Prepares the `(image, simple clinical note, ground truth)` dataset that the
agent workflow and the evaluation use. Aligned to the **14 VinBigData
competition classes** that our CV model (`app/workflow/tools/cv_model.py`)
predicts.

## Source

Public HuggingFace mirror of **VinDr-CXR**:
[`Benxelua/vindr-png-yolo-rescale`](https://huggingface.co/datasets/Benxelua/vindr-png-yolo-rescale)
— chest X-rays as 1024×1024 grayscale PNG plus YOLO-format bounding boxes.
No Kaggle account needed.

The mirror uses VinDr-CXR's **22 local labels**. The Kaggle competition (and our
CV model) use **14 classes**, which are a name-subset of the 22. We keep boxes
whose class is one of the 14 and drop the other 8 (Clavicle fracture, Edema,
Emphysema, Enlarged PA, Lung cavity, Lung cyst, Mediastinal shift, Rib fracture).

## Regenerate

```bash
# 1) Stage labels + image pointers (no large image bytes; ~80 MB).
mkdir -p data/_staging && cd data/_staging
GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 \
  https://huggingface.co/datasets/Benxelua/vindr-png-yolo-rescale vindr
cd ../..

# 2) Select a class-balanced subset, download those PNGs, emit the dataset.
python data/prepare_dataset.py                      # defaults: ~35/class + 80 no-finding
python data/prepare_dataset.py --per-class 50 --no-finding 120   # larger
python data/prepare_dataset.py --limit 12           # tiny smoke test
```

Runs in the project's Python env (needs `Pillow`). Re-running skips PNGs that
are already downloaded.

## Output (`data/vinbig/`)

| file | tracked in git | contents |
|------|----------------|----------|
| `dataset.json`    | yes | one entry per image (nested ground truth + note) |
| `annotations.csv` | yes | flat, one row per ground-truth box (+ no-finding rows) |
| `classes.json`    | yes | the 14 class names; list index == `class_id` |
| `images/*.png`    | **no** (gitignored) | the selected X-rays; re-fetch with the script |

Current build: **215 images** (135 abnormal + 80 no-finding), **1505 boxes**,
every one of the 14 classes covered (33–74 images each).

### `dataset.json` entry

```json
{
  "image_id": "001d127bad87592efe45a5c7678f8b8d",
  "image_path": "images/001d127bad87592efe45a5c7678f8b8d.png",
  "width": 1024,
  "height": 1024,
  "is_no_finding": false,
  "image_labels": ["Calcification", "Pulmonary fibrosis"],
  "clinical_note": "68-year-old male presenting with respiratory complaints. The radiograph shows ...",
  "ground_truth": [
    {"label": "Pulmonary fibrosis", "class_id": 13, "box": [356.4, 124.5, 432.7, 277.1]}
  ]
}
```

- **Boxes** are `[x_min, y_min, x_max, y_max]` in the **1024×1024 PNG pixel
  space** — the same space the CV tool returns, so detections and ground truth
  are directly comparable.
- **`clinical_note`** ("簡單病例") is **synthetic**, generated from the ground-truth
  labels as a short, consistent referral note. For evaluating the verify agent,
  inconsistent descriptions can be built from `image_labels` (swap in absent
  findings). Edit `FINDING_PHRASE` / `make_clinical_note` in the script to change
  the wording.
- VinDr-CXR is multi-radiologist, so an image can carry several overlapping boxes
  for the same finding (kept as-is; fuse with WBF downstream if a single box per
  finding is needed).
- A `No finding` image has empty `ground_truth` and one `class_id 14` row in the CSV.
