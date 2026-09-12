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
