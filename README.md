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

### 3) Docker Compose (backend + frontend)
This repository supports two Compose profiles:

- `dev`: FastAPI backend + Vite dev server (hot reload)
- `prod`: FastAPI backend + built frontend served by Nginx

Development profile:
```bash
docker compose --profile dev up --build
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

Production-like profile:
```bash
docker compose --profile prod up --build
```

- Frontend: http://localhost:8080
- Backend API: http://localhost:8000

Stop either profile:
```bash
docker compose --profile dev down
docker compose --profile prod down
```

If your machine has an NVIDIA GPU with the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) installed, uncomment the `deploy.resources.reservations` sections in `docker-compose.yml` to enable GPU acceleration.

### 4) Docker Compose (backend-only)
If you want to spin up only the backend API service using Docker Compose (without the frontend), you can run:

```bash
docker compose --profile dev up backend-dev --build
```

Because all services are configured with specific profiles, running `docker compose up` without specifying a profile or service will start no services.


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
