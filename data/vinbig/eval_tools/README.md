# MedAgentCV Automated Evaluation Pipeline

## Overview
This component provides an automated evaluation pipeline for the MedAgentCV project. It leverages an LLM-as-a-Judge architecture (powered by GPT-4o-mini) to evaluate the diagnostic accuracy of the medical AI agent against the VinBigData chest X-ray dataset. 

Instead of relying on rigid string matching or simple accuracy metrics, this pipeline extracts definitive imaging-backed diagnoses using a constrained vocabulary (Ontology Mapping) and calculates Precision, Recall, and F1-Score. This ensures the evaluation penalizes hallucinations (over-diagnosing based on patient descriptions) and accurately reflects clinical reliability.

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

```bash
source venv/bin/activate
pip install requests python-dotenv
```

## Usage

The evaluation pipeline is operated via the terminal. To prevent accidental API consumption, you must explicitly define the number of test cases to process.

### Arguments
* `-n`, `--num_cases` **(Required)**: An integer defining how many items from the dataset to evaluate.

### Examples

**1. Smoke Test (5 Cases)**
Ideal for verifying backend connectivity and pipeline logic without exhausting API credits.
```bash
python run_evaluation.py -n 5 | tee output.txt
```

**2. Run the Full Evaluation (All 215 cases):**
Use this command to process the entire dataset and generate the final performance metrics for the project.

```bash
python run_evaluation.py --num_cases 215 | tee output.txt
```

## Evaluation Metrics

Upon execution, the script outputs a terminal dashboard detailing the agent's performance. These metrics are specifically selected to evaluate imbalanced medical datasets:

* **Precision**: The ratio of accurate diagnoses to total predicted diagnoses. High precision indicates the agent effectively avoids false positives and hallucinations (i.e., it does not diagnose a condition based solely on patient claims without imaging proof).
* **Recall**: The ratio of accurate diagnoses to the actual ground truth. High recall signifies that the agent successfully detects critical findings and minimizes missed diagnoses (false negatives).
* **F1-Score**: The harmonic mean of Precision and Recall. This acts as the primary benchmark for the agent's overall diagnostic reliability and clinical safety.