# MedAgentCV Automated Evaluation Pipeline

## Overview
This component provides an automated evaluation pipeline for the MedAgentCV project. It leverages an LLM-as-a-Judge architecture (powered by GPT-4o-mini) to evaluate the diagnostic accuracy of the medical AI agent against the VinBigData chest X-ray dataset. 

Instead of relying on rigid string matching or simple accuracy metrics, this pipeline extracts definitive imaging-backed diagnoses using a constrained vocabulary (Ontology Mapping). It incorporates a robust checkpointing system to prevent data loss during API interruptions and calculates both Micro and Macro metrics (Precision, Recall, and F1-Score) to accurately reflect clinical reliability across both common and rare diseases.

## Prerequisites

Before running the evaluation script, ensure the following requirements are met:

### 1. Environment Configuration
Create a `.env` file in the root directory of the project and add your OpenAI API key. This key is required for the LLM-as-a-Judge functionality.

```env
OPENAI_API_KEY=sk-your-api-key-here
```

### 2. Backend Server
The evaluation script requires an active connection to the local API. Please ensure your FastAPI server or Docker container is up and running prior to execution.
* **Default Endpoint:** `http://127.0.0.1:8000`

### 3. Python Dependencies
It is highly recommended to run this script within a virtual environment. Activate your environment and install the required packages using pip:

#### (Required for the first time running)
```bash
python -m venv venv
pip install requests python-dotenv
```

#### (Required for every time running)
```bash
source venv/bin/activate
```


## Output System & Logging

The script features a built-in `DualLogger` and state manager, eliminating the need for manual shell redirection (e.g., `| tee`). Upon execution, an `output/` directory is automatically generated alongside the script to securely store all artifacts.

The following files are autonomously created and updated during runtime:
* `output/evaluation_log.txt`: A complete, real-time persistent mirror of your terminal output.
* `output/evaluation_checkpoint.json`: A continuous save-state of successful evaluations, enabling seamless resumption if the process is interrupted.

## Usage

The evaluation pipeline is operated via the terminal. To prevent accidental API credit exhaustion, the script enforces strict start and end boundaries.

### Command Line Arguments
You must select exactly one starting method (`--start` or `--resume`) and pair it with the required `--end` limit.

* `--start <int>`: Defines the starting case number (using a 1-based index).
* `--resume`: Automatically detects the last completed case from the checkpoint file and resumes execution from the next case.
* `--end <int>` **(Required)**: Defines the final case number to process. *Note: The dataset contains a maximum of 215 cases.*

### Execution Examples

**1. Smoke Test (First 5 Cases)**
Ideal for verifying your backend connection and pipeline logic without draining API credits.
```bash
python run_evaluation.py --start 1 --end 5
```

**2. Safe Resumption**
If your API connection drops or you manually interrupt the script, use this command to automatically pick up exactly where the last save-state left off.

```bash
python run_evaluation.py --resume --end 100
```


**3. Full Evaluation**
Run the complete dataset from start to finish to calculate your definitive project metrics.

```bash
python run_evaluation.py --start 1 --end 215
```

## Evaluation Metrics

Upon completion or manual interruption, the script outputs a comprehensive performance dashboard. These metrics are specifically chosen to handle the heavy class imbalances typical in medical datasets.

**Micro Metrics (Overall System Performance)**
Calculated globally across all predictions to reflect the agent's total diagnostic success rate.
* **Micro Precision**: The ratio of correct diagnoses to the total number of predicted diagnoses. A high score indicates the agent effectively avoids false positives and prevents AI hallucinations.
* **Micro Recall**: The ratio of correct diagnoses to the actual ground truth. A high score signifies that the agent reliably detects true findings and minimizes missed diagnoses (false negatives).
* **Micro F1-Score**: The harmonic mean of Micro Precision and Micro Recall.

**Macro Metrics (Class-Balanced Performance)**
Calculated independently for each of the 14 valid disease classes and then averaged.
**Macro Metrics (Class-Balanced Performance)**
Calculated independently for each of the 14 valid disease classes and then averaged. This ensures that every condition is weighted equally, regardless of its prevalence in the dataset.
* **Macro Precision**: Measures the model's average exactness across all disease types. A high score means the agent effectively avoids false positives even when evaluating highly rare conditions.
* **Macro Recall**: Measures the model's average sensitivity across all disease types. A high score signifies that the agent successfully detects rare diseases just as well as common ones.
* **Macro F1-Score**: The harmonic mean of Macro Precision and Macro Recall. A strong Macro F1 proves the model is comprehensively robust across the entire clinical spectrum and does not ignore rare anomalies.