# Website Backend (FastAPI)

A FastAPI backend service configured with CORS to work with frontend applications.

## Features

- FastAPI framework
- CORS middleware configured for localhost:3000
- Basic health check endpoint

## Setup

1. Install dependencies using uv:
```bash
uv sync
```

2. Run the development server:
```bash
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `GET /` - Health check endpoint that returns `{"ok": true}`

## Project Structure

```
website-backend-python/
├── app/
│   ├── __init__.py
│   └── main.py          # FastAPI application
├── pyproject.toml       # Project dependencies
├── uv.lock             # Lock file for dependencies
└── README.md
```

## Requirements

- Python 3.13+
- FastAPI
- Uvicorn

