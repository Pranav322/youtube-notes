# YouTube Technical Note-Taker

Convert YouTube videos into structured Markdown notes with preserved code blocks, formulas, and technical content.

## Features

- Map-Reduce AI processing for handling long videos without context loss
- Syntax-highlighted code blocks with copy button
- Smooth-scrolling Table of Contents
- PDF and Markdown export
- Rate limiting (2 videos per user, configurable admin bypass)

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI, Python 3.13 |
| Frontend | Next.js 16, TypeScript |
| AI | Azure OpenAI (GPT-4) |
| Database | PostgreSQL (Neon) |
| Deployment | Docker Compose |

## Prerequisites

- Docker and Docker Compose
- Azure OpenAI API access
- PostgreSQL database (Neon recommended)

## Setup

### 1. Clone and configure environment

```bash
git clone https://github.com/Pranav322/youtube-notes.git
cd youtube-notes
```

Create `.env` in the project root:

```env
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_DEPLOYMENT_NAME=gpt-4o
```

### 2. Run with Docker Compose

```bash
docker compose up --build -d
```

Access the application at `http://localhost:3000`

## Development

### Backend (without Docker)

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

### Frontend (without Docker)

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/notes` | Generate notes from YouTube URL |
| GET | `/notes/{id}` | Retrieve saved note |
| GET | `/health` | Health check |

### Request Example

```bash
curl -X POST http://localhost:8000/notes \
  -H "Content-Type: application/json" \
  -d '{"url": "https://youtube.com/watch?v=VIDEO_ID"}'
```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | SQLite (dev) |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL | Required |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | Required |
| `AZURE_DEPLOYMENT_NAME` | Model deployment name | gpt-4o |

## License

MIT
