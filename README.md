# Website Backend (FastAPI)

A FastAPI backend service configured with CORS to work with frontend applications.

## Features

- FastAPI framework
- CORS middleware configured for local development and production (zepedrocmota.com)
- Basic health check endpoint
- **Contact Form AI Assistant** - Generate and improve contact form messages
- **AI Debate Generator** - Generate debates between two AI agents on any topic with streaming responses
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

### General
- `GET /` - Health check endpoint that returns `{"ok": true}`

### Contact Form Assistant (`/api/contact`)
- `POST /api/contact/draft` - Generate a contact message draft
  - Request: `{ "name": string, "email": string, "subject": string }`
  - Response: `{ "draft": string }`
- `POST /api/contact/draft/improve` - Improve an existing draft
  - Request: `{ "draft": string, "comment": string }`
  - Response: `{ "draft": string }`

### Debate Generator (`/api/debate`)
- `POST /api/debate/generate` - Generate a streaming debate between two AI agents
  - Request: `{ "topic": string }`
  - Response: Server-Sent Events (SSE) stream
  - Each event: `{ "speaker": "debater_1"|"debater_2", "message": string, "position": string }`
  - Final event: `{ "done": true }`

## Project Structure

```
website-backend-python/
├── app/
│   ├── features/
│   │   ├── contact/
│   │   │   ├── router.py    # Contact form endpoints
│   │   │   └── service.py   # Contact form business logic
│   │   └── debate/
│   │       ├── router.py    # Debate endpoints
│   │       └── service.py   # Debate generation logic
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── llm_agent.py         # LLM agent configuration
│   └── settings.py          # Application settings
├── pyproject.toml           # Project dependencies
├── uv.lock                  # Lock file for dependencies
└── README.md
```

## Requirements

- Python 3.12+
- FastAPI
- Uvicorn
- OpenAI compatible API (configured for Groq)
- OpenAI Agents library

## Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
OPENAI_BASE_URL=https://api.groq.com/openai/v1
ENV=development
```

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

