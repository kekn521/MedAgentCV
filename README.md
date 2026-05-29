# MedAgentCV
Intro to Artificial Intelligence Term Project

## Local setup

### 1) Create env file
Copy the example and fill in your OpenAI key:

```bash
copy .env.example .env
```

Then edit `.env` with your values.

### 2) Install dependencies
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

If you prefer a plain requirements install for a one-off run, use `pip install -r requirements.txt` after activating the environment.

### 3) Run the API
```bash
uvicorn app.main:app --reload
```

The API will be available at: http://127.0.0.1:8000

## Docker setup

### 1) Create env file
Copy the example and fill in your OpenAI key:

```bash
copy .env.example .env
```

Then edit `.env` with your values.

### 2) Build and run (Docker)
```bash
docker build -t medagentcv .
docker run --env-file .env -p 8000:8000 medagentcv
```

### 3) Docker Compose (optional)
```bash
docker compose up --build
```

### API usage
POST `/api/v1/analyze` (multipart/form-data):
- `image`: image file
- `disease_description`: text (optional)

## Frontend setup

The frontend is a React + Vite single-page app in `frontend/` that lets you
upload a chest X-ray, run the agent, and view the input/output (detection boxes,
final analysis, and the internal analytic ↔ verify dialogue).

### 1) Install dependencies
```bash
cd frontend
npm install
```

### 2) Run the dev server
```bash
npm run dev
```

The app will be available at: http://localhost:5173

The dev server proxies `/api` to the backend at `http://127.0.0.1:8000`, so make
sure the API (above) is running. Then upload an image (a description is optional)
and click **Run Analysis**.

> No backend running? Click **Load sample result** in the header to preview the
> interface with mock data — no API key required.

### 3) Production build (optional)
```bash
npm run build
npm run preview
```
