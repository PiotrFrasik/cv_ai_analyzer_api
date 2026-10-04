# CV AI ANALYZER API

CV AI Analyzer is a robust Django REST Framework application that automatically scores candidates' CVs against job offers utilizing the Google Gemini API. The entire system is containerized with Docker, uses PostgreSQL for data storage, and relies on Celery with Redis for efficient background task processing.

## Live Demo

**Swagger UI:** [https://kuriozum.bieda.it/cv_ai-analyzer-api/](https://kuriozum.bieda.it/cv_ai-analyzer-api/)

## Setup

Copy `.env.example` to `.env` and fill in the values, then:

```bash
docker compose up --build
```

Migrations run automatically on container start. Swagger docs available at `http://localhost:8001/api/docs/`.

## Testing

```bash
docker compose exec web python manage.py test --noinput
```

Or using a one-off container:

```bash
docker compose run --rm web python manage.py test --noinput
```

## API

```
POST   /api/user/register/
POST   /api/token/
POST   /api/token/refresh/

POST   /api/documents/cv/create/
GET    /api/documents/cv/<id>/
GET    /api/documents/cv/

POST   /api/documents/job-offer/create/
GET    /api/documents/job-offer/<id>/
GET    /api/documents/job-offer/

GET    /api/analysis/
GET    /api/analysis/<id>/
```

## Architecture

When a CV or Job Offer is created, the system automatically pairs matching documents and dispatches a Celery task (`run_ai_analysis`) to score them via Google Gemini.

**Analysis flow:** Upload CV/Job Offer → create `Analysis` record (`pending`) → dispatch Celery task → worker calls Gemini API → save score and missing skills (`done`).

**Analysis statuses:** `pending` → `processing` → `done` | `failed`.

**Retry policy:** Tasks retry up to 3 times with exponential backoff (capped at 10 min) and randomized jitter. The Gemini client has a 30s timeout to prevent hanging workers.

**Idempotency:** A `UniqueConstraint(cv, job_offer)` prevents duplicate analyses. The task acquires a row lock (`select_for_update`) and skips execution if the status is already `processing` or `done`, so duplicate task deliveries never trigger redundant paid API calls.

**File Upload Constraints:** CV uploads (`POST /api/documents/cv/create/`) are strictly validated for `.pdf` file extension and limited to a maximum file size of 5 MB (`DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880`).

## Observability

All Celery worker activity is logged to stdout/stderr and visible via:

```bash
docker compose logs celery -f
```

Each analysis task logs its lifecycle — task received, status transitions (`pending → processing → done/failed`), Gemini response time, and retry attempts. To inspect what a worker did for a specific analysis:

```bash
docker compose logs celery | grep "analysis_id=<id>"
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.