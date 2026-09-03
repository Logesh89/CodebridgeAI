# SnapLogic to Python AI Conversion Platform

Enterprise-grade web application that automatically converts SnapLogic pipelines into Pure Python code using AI, validates outputs, and provides complete monitoring and workflow orchestration.

## Architecture

```
snaplogic-python-platform/
├── frontend/          # React 19 + TypeScript + Vite + Material UI
├── backend/           # FastAPI + Python 3.12 + SQLAlchemy
├── database/          # PostgreSQL init scripts
├── airflow/           # Apache Airflow DAGs
├── datadog/           # Datadog monitoring config
├── docker/            # Dockerfiles
├── uploads/           # Excel uploads
├── snaplogic_json/    # Original SnapLogic definitions
├── generated/         # AI-generated Python (temp)
├── completed/         # Successful conversions
├── failed/            # Failed conversions
├── logs/              # Application logs
├── reports/           # Validation reports (HTML/PDF/JSON)
├── tests/             # Pytest test suite
└── docs/              # Documentation
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript, Vite, Material UI, React Query |
| Backend | FastAPI, Python 3.12, SQLAlchemy, Alembic, Pydantic |
| Database | PostgreSQL |
| Auth | Email OTP, JWT, Refresh Tokens, Bcrypt |
| Workflow | Apache Airflow |
| Monitoring | Datadog |
| Container | Docker, Docker Compose |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 22+ (local frontend dev)
- Python 3.12+ (local backend dev)

### Setup

```bash
# Clone and configure
cp .env.example .env
# Edit .env with your SnapLogic, OpenAI, SMTP, and Datadog credentials

# Start all services
docker-compose up -d

# Or run locally:

# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

### Access

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| Airflow | http://localhost:8080 |

## Application Flow

1. **Login** → Email + OTP verification → JWT token
2. **Upload Excel** → Validate pipeline paths
3. **Fetch SnapLogic** → Download JSON/XML definitions
4. **AI Conversion** → Generate Pure Python code
5. **Execute Both** → Run SnapLogic and Python pipelines
6. **Validate** → Compare outputs (row count, columns, types, values, checksums)
7. **Store Results** → Move to `completed/` or `failed/`
8. **Notify** → Email and in-app notifications

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | Send OTP to email |
| POST | `/api/v1/auth/verify-otp` | Verify OTP, get JWT |
| POST | `/api/v1/auth/logout` | Logout |
| GET | `/api/v1/dashboard` | Dashboard metrics |
| POST | `/api/v1/excel/upload` | Upload Excel file |
| GET | `/api/v1/pipelines` | List pipelines |
| POST | `/api/v1/pipelines/{id}/convert` | Start conversion |
| GET | `/api/v1/reports` | Validation reports |
| GET | `/api/v1/logs` | System logs |
| GET | `/api/v1/notifications` | User notifications |

## Roles

- **Admin** — Full system access, user management
- **Developer** — Upload, convert, execute pipelines
- **Viewer** — Read-only dashboard and reports

## Testing

```bash
cd backend
pip install pytest pytest-asyncio aiosqlite httpx
pytest ../tests/backend/ -v
```

## Environment Variables

See `.env.example` for all configuration options including:
- PostgreSQL connection
- JWT secrets
- SMTP for email/OTP
- SnapLogic API credentials
- OpenAI API key for AI conversion
- Datadog API keys

## License

Proprietary — All rights reserved.
