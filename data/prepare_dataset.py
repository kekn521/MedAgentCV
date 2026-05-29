"""Prepare a VinBigData (VinDr-CXR) detection dataset for MedAgentCV.

Turns the public HuggingFace mirror `Benxelua/vindr-png-yolo-rescale`
(VinDr-CXR as 1024px PNG + YOLO labels, 22 local labels) into the
(image, simple clinical note, ground truth) dataset our agent + evaluation use.

Output, aligned to the 14 VinBigData competition classes that
`app/workflow/tools/cv_model.py` predicts:

  data/vinbig/
    images/<image_id>.png          selected chest X-rays (1024x1024 grayscale)
    dataset.json                   one entry per image (nested ground truth + note)
    annotations.csv                flat, one row per ground-truth box (+ no-finding rows)
    classes.json                   the 14 class names (index == class_id)

Pipeline: select a class-balanced subset from the staged labels, download only
those PNGs, then emit the records. Re-running is cheap (downloads are skipped if
the PNG already exists).

Usage (from repo root, inside the ml env):
    python data/prepare_dataset.py                 # default subset
    python data/prepare_dataset.py --per-class 40 --no-finding 80
    python data/prepare_dataset.py --limit 12      # tiny smoke test
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import random
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
STAGING_LABELS = HERE / "_staging" / "vindr" / "labels" / "train"
STAGING_IMAGES = HERE / "_staging" / "vindr" / "images" / "train"
OUT_DIR = HERE / "vinbig"
IMG_DIR = OUT_DIR / "images"

HF_REPO = "Benxelua/vindr-png-yolo-rescale"
HF_IMAGE_URL = (
    "https://huggingface.co/datasets/" + HF_REPO + "/resolve/main/images/train/{stem}.png"
)

# Source dataset: VinDr-CXR 22 local labels (class id == list index), from data.yaml.
NAMES_22 = [
    "Aortic enlargement", "Atelectasis", "Calcification", "Cardiomegaly",
    "Clavicle fracture", "Consolidation", "Edema", "Emphysema", "Enlarged PA",
    "ILD", "Infiltration", "Lung Opacity", "Lung cavity", "Lung cyst",
    "Mediastinal shift", "Nodule/Mass", "Other lesion", "Pleural effusion",
    "Pleural thickening", "Pneumothorax", "Pulmonary fibrosis", "Rib fracture",
]

# Target: the 14 Kaggle VinBigData classes our CV model predicts (class id == index).
# Must stay byte-for-byte identical to CLASS_NAMES in app/workflow/tools/cv_model.py.
CLASS_NAMES_14 = [
    "Aortic enlargement", "Atelectasis", "Calcification", "Cardiomegaly",
    "Consolidation", "ILD", "Infiltration", "Lung Opacity", "Nodule/Mass",
    "Other lesion", "Pleural effusion", "Pleural thickening", "Pneumothorax",
    "Pulmonary fibrosis",
]
NAME_TO_ID14 = {name: i for i, name in enumerate(CLASS_NAMES_14)}

# Short clinical phrase per finding, used to synthesize the simple case note.
FINDING_PHRASE = {
    "Aortic enlargement": "a widened aortic contour",
    "Atelectasis": "a band of atelectasis",
    "Calcification": "focal calcification",
    "Cardiomegaly": "an enlarged cardiac silhouette",
    "Consolidation": "an area of consolidation",
    "ILD": "reticular changes suggesting interstitial lung disease",
    "Infiltration": "a pulmonary infiltrate",
    "Lung Opacity": "a focal lung opacity",
    "Nodule/Mass": "a pulmonary nodule/mass",
    "Other lesion": "an additional lesion of uncertain nature",
    "Pleural effusion": "blunting of the costophrenic angle suggesting pleural effusion",
    "Pleural thickening": "pleural thickening",
    "Pneumothorax": "a possible pneumothorax",
    "Pulmonary fibrosis": "fibrotic streaking suggesting pulmonary fibrosis",
}


def parse_label_file(path: Path):
    """YOLO lines -> list of (name22, xc, yc, w, h) in normalized coords."""
    rows = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        cid, xc, yc, w, h = line.split()[:5]
        rows.append((NAMES_22[int(float(cid))], float(xc), float(yc), float(w), float(h)))
    return rows


def image_label_set(path: Path):
    """The 14-class finding names present in a label file (dropped classes ignored)."""
    return {n for (n, *_rest) in parse_label_file(path) if n in NAME_TO_ID14}


def select_subset(per_class: int, n_no_finding: int, seed: int, limit: int | None):
    """Pick a class-balanced set of image stems from the staged labels.

    Greedy from rarest class to commonest so scarce findings (e.g. Pneumothorax)
    are not crowded out by images that also carry common ones.
    """
    rng = random.Random(seed)
    # Only consider stems whose non-aug PNG pointer exists in the staging clone,
    # so every selected image has a real download URL (avoids 404s).
    have_image = {Path(p).stem for p in glob.glob(str(STAGING_IMAGES / "*.png"))
                  if "_aug" not in os.path.basename(p)}
    files = [Path(p) for p in glob.glob(str(STAGING_LABELS / "*.txt"))
             if "_aug" not in os.path.basename(p) and Path(p).stem in have_image]

    abnormal, no_finding, only_dropped = {}, [], set()
    for fp in files:
        labels = image_label_set(fp)
        if labels:
            abnormal[fp.stem] = labels
        elif parse_label_file(fp):
            only_dropped.add(fp.stem)  # had boxes, but only non-14 classes
        else:
            no_finding.append(fp.stem)

    by_class = {c: [] for c in CLASS_NAMES_14}
    for stem, labels in abnormal.items():
        for c in labels:
            by_class[c].append(stem)

    selected = set()
    for cls in sorted(CLASS_NAMES_14, key=lambda c: len(by_class[c])):
        pool = by_class[cls][:]
        rng.shuffle(pool)
        have = sum(1 for s in selected if cls in abnormal[s])
        for stem in pool:
            if have >= per_class:
                break
            if stem not in selected:
                selected.add(stem)
                have += 1

    nf = no_finding[:]
    rng.shuffle(nf)
    nf = nf[:n_no_finding]

    stems = sorted(selected) + nf
    if limit:
        keep_abnormal = sorted(selected)[: max(1, limit // 2)]
        keep_nf = nf[: limit - len(keep_abnormal)]
        stems = keep_abnormal + keep_nf
    return stems, {
        "total_label_files": len(files),
        "abnormal_available": len(abnormal),
        "no_finding_available": len(no_finding),
        "only_dropped_available": len(only_dropped),
        "selected_abnormal": len([s for s in stems if s in abnormal]),
        "selected_no_finding": len([s for s in stems if s in no_finding]),
    }


def download_images(stems, workers: int):
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    todo = [s for s in stems if not (IMG_DIR / f"{s}.png").exists()]
    if not todo:
        print(f"  all {len(stems)} images already present, skipping download")
        return

    def fetch(stem):
        dest = IMG_DIR / f"{stem}.png"
        req = urllib.request.Request(HF_IMAGE_URL.format(stem=stem),
                                     headers={"User-Agent": "medagentcv-dataprep"})
        with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
            f.write(r.read())
        return stem

    done = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(fetch, s): s for s in todo}
        for fut in as_completed(futures):
            stem = futures[fut]
            try:
                fut.result()
                done += 1
                if done % 25 == 0 or done == len(todo):
                    print(f"  downloaded {done}/{len(todo)}")
            except Exception as e:  # noqa: BLE001 - skip a bad image, keep going
                print(f"  WARN failed {stem}: {e}")
                (IMG_DIR / f"{stem}.png").unlink(missing_ok=True)


def yolo_to_xyxy(xc, yc, w, h, W, H):
    x1 = (xc - w / 2) * W
    y1 = (yc - h / 2) * H
    x2 = (xc + w / 2) * W
    y2 = (yc + h / 2) * H
    clamp = lambda v, hi: round(float(max(0, min(v, hi))), 1)
    return [clamp(x1, W), clamp(y1, H), clamp(x2, W), clamp(y2, H)]


def make_clinical_note(labels, rng):
    """A short, plausible referral note that names the findings (consistent case)."""
    age = rng.randint(28, 81)
    sex = rng.choice(["male", "female"])
    if not labels:
        return (f"{age}-year-old {sex} for a routine chest radiograph. "
                "No specific cardiopulmonary complaint reported.")
    phrases = [FINDING_PHRASE[c] for c in labels]
    if len(phrases) == 1:
        body = phrases[0]
    else:
        body = ", ".join(phrases[:-1]) + " and " + phrases[-1]
    lead = rng.choice([
        f"{age}-year-old {sex} presenting with respiratory complaints.",
        f"Chest X-ray requested for a {age}-year-old {sex}.",
        f"{age}-year-old {sex} referred for thoracic imaging.",
    ])
    return f"{lead} The radiograph shows {body}. Please review."


def build_records(stems, seed):
    rng = random.Random(seed)
    records = []
    for stem in sorted(stems):
        img_path = IMG_DIR / f"{stem}.png"
        label_path = STAGING_LABELS / f"{stem}.txt"
        if not img_path.exists():
            continue
        with Image.open(img_path) as im:
            W, H = im.size
        gt = []
        present = []
        for (name22, xc, yc, w, h) in parse_label_file(label_path):
            if name22 not in NAME_TO_ID14:
                continue
            cid = NAME_TO_ID14[name22]
            gt.append({"label": name22, "class_id": cid,
                       "box": yolo_to_xyxy(xc, yc, w, h, W, H)})
            present.append(name22)
        image_labels = sorted(set(present), key=lambda n: NAME_TO_ID14[n])
        records.append({
            "image_id": stem,
            "image_path": f"images/{stem}.png",
            "width": W,
            "height": H,
            "is_no_finding": len(gt) == 0,
            "image_labels": image_labels,
            "clinical_note": make_clinical_note(image_labels, rng),
            "ground_truth": gt,
        })
    return records


def write_outputs(records):
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    (OUT_DIR / "classes.json").write_text(
        json.dumps({"class_names": CLASS_NAMES_14}, indent=2, ensure_ascii=False))

    (OUT_DIR / "dataset.json").write_text(
        json.dumps(records, indent=2, ensure_ascii=False))

    with open(OUT_DIR / "annotations.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["image_id", "image_path", "width", "height",
                    "is_no_finding", "clinical_note",
                    "class_name", "class_id", "x_min", "y_min", "x_max", "y_max"])
        for r in records:
            if r["is_no_finding"]:
                w.writerow([r["image_id"], r["image_path"], r["width"], r["height"],
                            True, r["clinical_note"], "No finding", 14, "", "", "", ""])
                continue
            for b in r["ground_truth"]:
                x1, y1, x2, y2 = b["box"]
                w.writerow([r["image_id"], r["image_path"], r["width"], r["height"],
                            False, r["clinical_note"],
                            b["label"], b["class_id"], x1, y1, x2, y2])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--per-class", type=int, default=35,
                    help="target images per 14-class finding (default 35)")
    ap.add_argument("--no-finding", type=int, default=80,
                    help="number of No-finding images to include (default 80)")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--limit", type=int, default=None,
                    help="cap total images (smoke test)")
    args = ap.parse_args()

    if not STAGING_LABELS.exists():
        raise SystemExit(
            f"Staged labels not found at {STAGING_LABELS}.\n"
            "Run the staging clone first (see data/README.md).")

    print("[1/4] selecting class-balanced subset ...")
    stems, stats = select_subset(args.per_class, args.no_finding, args.seed, args.limit)
    print(f"      selected {len(stems)} images  {stats}")

    print("[2/4] downloading PNGs ...")
    download_images(stems, args.workers)

    print("[3/4] building records ...")
    records = build_records(stems, args.seed)

    print("[4/4] writing outputs ...")
    write_outputs(records)

    n_box = sum(len(r["ground_truth"]) for r in records)
    n_nf = sum(1 for r in records if r["is_no_finding"])
    print(f"done. {len(records)} images ({n_nf} no-finding), {n_box} ground-truth boxes")
    print(f"  -> {OUT_DIR/'dataset.json'}")
    print(f"  -> {OUT_DIR/'annotations.csv'}")


if __name__ == "__main__":
    main()
