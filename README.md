# CV AI ANALYZER API

CV AI Analyzer is a robust Django REST Framework application that automatically scores candidates' CVs against job offers utilizing the Google Gemini API. The entire system is containerized with Docker, uses PostgreSQL for data storage, and relies on Celery with Redis for efficient background task processing.

## Setup

Copy `.env.example` to `.env` and fill in the values, then:

```bash
docker compose up --build
docker exec django-cv python manage.py migrate
```

Swagger docs available at `http://localhost:8000/api/docs/`.

## API

```
POST   /api/user/register/
POST   /api/token/
POST   /api/token/refresh/

POST   /api/cv/create/
GET    /api/cv/<id>/

POST   /api/job_offer/create/
GET    /api/job_offer/<id>/

GET    /api/analysis/
GET    /api/analysis/<id>/
```

## Architecture

When a CV or Job Offer is created, the system automatically pairs matching documents and dispatches a Celery task (`run_ai_analysis`) to score them via Google Gemini.

**Analysis flow:** Upload CV/Job Offer → create `Analysis` record (`pending`) → dispatch Celery task → worker calls Gemini API → save score and missing skills (`done`).

**Analysis statuses:** `pending` → `processing` → `done` | `failed`.

**Retry policy:** Tasks retry up to 3 times with exponential backoff (capped at 10 min) and randomized jitter. The Gemini client has a 30s timeout to prevent hanging workers.

**Idempotency:** A `UniqueConstraint(cv, job_offer)` prevents duplicate analyses. The task acquires a row lock (`select_for_update`) and skips execution if the status is already `processing` or `done`, so duplicate task deliveries never trigger redundant paid API calls.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

