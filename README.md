# Website Backend (FastAPI)

A FastAPI backend service configured with CORS to work with frontend applications.

## Features

- FastAPI framework
- CORS middleware configured for local development and production (zepedrocmota.com)
- Basic health check endpoint
- Ready for Vercel serverless deployment

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

- Python 3.12+
- FastAPI
- Uvicorn

## Deployment to Vercel

This project is configured for deployment to Vercel as a serverless function.

### Files for Vercel Deployment

- `requirements.txt` - Python dependencies for Vercel
- `vercel.json` - Vercel configuration specifying the Python runtime and routes

### Manual Deployment Steps

1. Push your code to a GitHub repository
2. Connect your repository to Vercel via the Vercel dashboard
3. Vercel will automatically detect the configuration and deploy
4. Your API will be available at your Vercel domain
5. FastAPI automatic docs will be available at `/docs`

### CORS Configuration

The app is configured to accept requests from:
- `http://localhost:3000` (local development)
- `https://www.zepedrocmota.com` (production)
- `https://zepedrocmota.com` (production without www)

