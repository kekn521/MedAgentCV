# CV Tool — VinBigData Chest X-ray Detection

## 用的模型

[`mserrasa/detr-resnet-50_finetuned_VinBigData`](https://huggingface.co/mserrasa/detr-resnet-50_finetuned_VinBigData)

- DETR + ResNet-50，已在 Kaggle [VinBigData Chest X-ray Abnormalities Detection](https://www.kaggle.com/competitions/vinbigdata-chest-xray-abnormalities-detection) 競賽資料上 fine-tune
- 41.6M 參數，Apache 2.0
- Object detection（label + bbox + score），對齊 VinBigData 14 個 abnormality class
- 首次呼叫從 HF 自動下載 weights，之後 cache 在 `~/.cache/huggingface`（Docker 是 named volume `hf_cache`）

## API contract

LangGraph tool 名稱：`vinbigdata_cv`

**輸入**：`image_path: str`（本地檔案路徑，需要先轉檔用Tiff會噴error，可以用PNG/JPG）

**輸出**：JSON 字串(我設計使用Json)
```json
{
  "findings": [
    {"label": "Cardiomegaly", "score": 0.87, "box": [x1, y1, x2, y2]},
    {"label": "Pleural effusion", "score": 0.76, "box": [x1, y1, x2, y2]}
  ]
}
```
- `findings` 已按 `score` 降冪排序
- bbox 是原圖座標（pixels）
- 預設 `SCORE_THRESHOLD = 0.3`，要調在 `app/workflow/tools/cv_model.py`

**Class label 對照**（給Evaluation）：
```python
from app.workflow.tools.cv_model import _load
_, model = _load()
print(model.config.id2label)
```

## 給其他組的注意事項

| 組別 | 注意事項 |
|---|---|
| Part 1 (Data) | image_path 直接丟，但要先轉 PNG/JPG。CSV 的 class name 可以用 `model.config.id2label` 對齊 |
| Part 4 (Eval) | 14 class label 從 `model.config.id2label` 取；mAP / IoU 計算可以用 `findings[].box` 對 VinBigData GT bbox |

## 變更檔案

- `app/workflow/tools/cv_model.py` — 從 mock 換成真 DETR inference
- `app/workflow/agents/analytic.py` — import 從 `mock_vinbigdata_cv` → `vinbigdata_cv`
- `requirements.txt` — 加 `transformers`、`timm`、`Pillow`（torch 走 base image）
- `Dockerfile` — base image 換 `pytorch/pytorch:2.11.0-cuda12.8-cudnn9-runtime`，原生支援 RTX 50-series (Blackwell sm_120)
- `docker-compose.yml` —  GPU + `hf_cache` named volume 持久化 model weights

## how to run
基本上Docker 直接跑就可以了
**Docker**
```bash
docker compose up --build -d
docker compose exec backend python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

**測試 endpoint**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/analyze \
  -F "image=@/path/to/xray.png" \
  -F "disease_description=patient with persistent cough"
```

## 備註

- 首次 build 後第一次呼叫會去下載權重檔
- Threshold 0.3 是預設值，沒做 per-class 調整；Evaluation 那組可能要做 threshold sweep
